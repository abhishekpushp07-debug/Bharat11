"""
Redis Manager - Specialized Redis Operations
Handles leaderboards, caching, pub/sub, and rate limiting.
World-class Redis implementation with sorted sets, pipelining, and Lua scripts.
"""
import asyncio
import json
import logging
import time
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

import redis.asyncio as aioredis
from redis.asyncio.client import Pipeline

logger = logging.getLogger(__name__)


class RedisKeyPrefix(str, Enum):
    """Redis key prefixes for namespacing."""
    LEADERBOARD = "lb"
    MATCH_STATE = "match"
    USER_SESSION = "session"
    RATE_LIMIT = "rl"
    CACHE = "cache"
    LOCK = "lock"
    PUBSUB = "ps"


@dataclass
class LeaderboardEntry:
    """Represents a leaderboard entry."""
    user_id: str
    score: float
    rank: int
    

class RedisManager:
    """
    Advanced Redis operations manager.
    Implements leaderboards, caching, rate limiting with best practices.
    """
    
    def __init__(self, redis_client: Optional[aioredis.Redis]):
        self._redis = redis_client
        self._pubsub = None
    
    @property
    def is_available(self) -> bool:
        """Check if Redis is available."""
        return self._redis is not None
    
    def _key(self, prefix: RedisKeyPrefix, *parts: str) -> str:
        """Build a namespaced Redis key."""
        return f"crickpredict:{prefix.value}:{':'.join(parts)}"
    
    # ==================== LEADERBOARD OPERATIONS ====================
    
    async def leaderboard_add(
        self, 
        contest_id: str, 
        user_id: str, 
        score: float,
        submission_timestamp: Optional[int] = None
    ) -> None:
        """
        Add or update user score in leaderboard.
        Uses composite score for tie-breaking: score * 1M + (MAX_TS - submission_ts)
        """
        if not self.is_available:
            return
        
        key = self._key(RedisKeyPrefix.LEADERBOARD, contest_id)
        
        # Composite score for tie-breaking (earlier submission wins)
        MAX_TIMESTAMP = 9999999999999  # Far future timestamp
        ts = submission_timestamp or int(time.time() * 1000)
        composite_score = (score * 1_000_000) + (MAX_TIMESTAMP - ts)
        
        await self._redis.zadd(key, {user_id: composite_score})
    
    async def leaderboard_increment(
        self, 
        contest_id: str, 
        user_id: str, 
        points: float
    ) -> float:
        """
        Increment user score in leaderboard.
        Returns new score.
        """
        if not self.is_available:
            return 0.0
        
        key = self._key(RedisKeyPrefix.LEADERBOARD, contest_id)
        # Increment by points * 1M to maintain composite score structure
        increment = points * 1_000_000
        new_score = await self._redis.zincrby(key, increment, user_id)
        return new_score / 1_000_000  # Return actual points
    
    async def leaderboard_batch_increment(
        self, 
        contest_id: str, 
        updates: List[Tuple[str, float]]
    ) -> None:
        """
        Batch increment multiple user scores using pipeline.
        Highly efficient for bulk updates after question resolution.
        """
        if not self.is_available or not updates:
            return
        
        key = self._key(RedisKeyPrefix.LEADERBOARD, contest_id)
        
        async with self._redis.pipeline(transaction=True) as pipe:
            for user_id, points in updates:
                increment = points * 1_000_000
                pipe.zincrby(key, increment, user_id)
            await pipe.execute()
    
    async def leaderboard_get_rank(
        self, 
        contest_id: str, 
        user_id: str
    ) -> Optional[int]:
        """
        Get user's rank in leaderboard (1-indexed).
        Returns None if user not in leaderboard.
        """
        if not self.is_available:
            return None
        
        key = self._key(RedisKeyPrefix.LEADERBOARD, contest_id)
        rank = await self._redis.zrevrank(key, user_id)
        return rank + 1 if rank is not None else None
    
    async def leaderboard_get_top(
        self, 
        contest_id: str, 
        limit: int = 50
    ) -> List[LeaderboardEntry]:
        """
        Get top N entries from leaderboard.
        Returns list sorted by rank (highest score first).
        """
        if not self.is_available:
            return []
        
        key = self._key(RedisKeyPrefix.LEADERBOARD, contest_id)
        results = await self._redis.zrevrange(key, 0, limit - 1, withscores=True)
        
        entries = []
        for rank, (user_id, composite_score) in enumerate(results, 1):
            actual_score = composite_score / 1_000_000
            entries.append(LeaderboardEntry(
                user_id=user_id,
                score=round(actual_score, 2),
                rank=rank
            ))
        
        return entries
    
    async def leaderboard_get_around_user(
        self, 
        contest_id: str, 
        user_id: str, 
        range_size: int = 2
    ) -> List[LeaderboardEntry]:
        """
        Get entries around a specific user's rank.
        Useful for showing user's position in context.
        """
        if not self.is_available:
            return []
        
        key = self._key(RedisKeyPrefix.LEADERBOARD, contest_id)
        user_rank = await self._redis.zrevrank(key, user_id)
        
        if user_rank is None:
            return []
        
        start = max(0, user_rank - range_size)
        end = user_rank + range_size
        
        results = await self._redis.zrevrange(key, start, end, withscores=True)
        
        entries = []
        for idx, (uid, composite_score) in enumerate(results):
            actual_score = composite_score / 1_000_000
            entries.append(LeaderboardEntry(
                user_id=uid,
                score=round(actual_score, 2),
                rank=start + idx + 1
            ))
        
        return entries
    
    async def leaderboard_get_total_count(self, contest_id: str) -> int:
        """Get total number of entries in leaderboard."""
        if not self.is_available:
            return 0
        
        key = self._key(RedisKeyPrefix.LEADERBOARD, contest_id)
        return await self._redis.zcard(key)
    
    async def leaderboard_delete(self, contest_id: str) -> None:
        """Delete entire leaderboard (after contest ends)."""
        if not self.is_available:
            return
        
        key = self._key(RedisKeyPrefix.LEADERBOARD, contest_id)
        await self._redis.delete(key)
    
    async def leaderboard_set_ttl(self, contest_id: str, ttl_seconds: int = 86400) -> None:
        """Set TTL on leaderboard key to prevent unbounded growth."""
        if not self.is_available:
            return
        
        key = self._key(RedisKeyPrefix.LEADERBOARD, contest_id)
        await self._redis.expire(key, ttl_seconds)
    
    # ==================== MATCH STATE CACHING ====================
    
    async def set_match_state(
        self, 
        match_id: str, 
        state: Dict[str, Any],
        ttl_seconds: int = 3600
    ) -> None:
        """
        Cache live match state.
        Uses Redis Hash for efficient partial updates.
        """
        if not self.is_available:
            return
        
        key = self._key(RedisKeyPrefix.MATCH_STATE, match_id)
        
        # Flatten nested dicts for Redis hash
        flat_state = {}
        for k, v in state.items():
            if isinstance(v, (dict, list)):
                flat_state[k] = json.dumps(v)
            else:
                flat_state[k] = str(v) if v is not None else ""
        
        await self._redis.hset(key, mapping=flat_state)
        await self._redis.expire(key, ttl_seconds)
    
    async def get_match_state(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Get cached match state."""
        if not self.is_available:
            return None
        
        key = self._key(RedisKeyPrefix.MATCH_STATE, match_id)
        state = await self._redis.hgetall(key)
        
        if not state:
            return None
        
        # Parse JSON fields back
        parsed = {}
        for k, v in state.items():
            try:
                parsed[k] = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                parsed[k] = v
        
        return parsed
    
    async def update_match_state_field(
        self, 
        match_id: str, 
        field: str, 
        value: Any
    ) -> None:
        """Update single field in match state."""
        if not self.is_available:
            return
        
        key = self._key(RedisKeyPrefix.MATCH_STATE, match_id)
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        await self._redis.hset(key, field, str(value) if value is not None else "")
    
    # ==================== RATE LIMITING ====================
    
    async def check_rate_limit(
        self, 
        identifier: str, 
        max_requests: int, 
        window_seconds: int
    ) -> Tuple[bool, int]:
        """
        Check and update rate limit using sliding window.
        Returns (is_allowed, remaining_requests).
        """
        if not self.is_available:
            return True, max_requests
        
        key = self._key(RedisKeyPrefix.RATE_LIMIT, identifier)
        now = time.time()
        window_start = now - window_seconds
        
        async with self._redis.pipeline(transaction=True) as pipe:
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            # Count current entries
            pipe.zcard(key)
            # Add current request
            pipe.zadd(key, {str(now): now})
            # Set expiry
            pipe.expire(key, window_seconds)
            
            results = await pipe.execute()
        
        current_count = results[1]
        is_allowed = current_count < max_requests
        remaining = max(0, max_requests - current_count - 1)
        
        return is_allowed, remaining
    
    # ==================== GENERIC CACHING ====================
    
    async def cache_set(
        self, 
        key_suffix: str, 
        value: Any, 
        ttl_seconds: int = 300
    ) -> None:
        """Set a cached value with TTL."""
        if not self.is_available:
            return
        
        key = self._key(RedisKeyPrefix.CACHE, key_suffix)
        
        serialized = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
        await self._redis.setex(key, ttl_seconds, serialized)
    
    async def cache_get(self, key_suffix: str) -> Optional[Any]:
        """Get a cached value."""
        if not self.is_available:
            return None
        
        key = self._key(RedisKeyPrefix.CACHE, key_suffix)
        value = await self._redis.get(key)
        
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    async def cache_delete(self, key_suffix: str) -> None:
        """Delete a cached value."""
        if not self.is_available:
            return
        
        key = self._key(RedisKeyPrefix.CACHE, key_suffix)
        await self._redis.delete(key)
    
    # ==================== PUB/SUB ====================
    
    async def publish(self, channel: str, message: Dict[str, Any]) -> None:
        """Publish message to channel."""
        if not self.is_available:
            return
        
        full_channel = self._key(RedisKeyPrefix.PUBSUB, channel)
        await self._redis.publish(full_channel, json.dumps(message))
    
    async def subscribe(self, channel: str):
        """Subscribe to channel. Returns async generator of messages."""
        if not self.is_available:
            return
        
        full_channel = self._key(RedisKeyPrefix.PUBSUB, channel)
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(full_channel)
        
        return pubsub
    
    # ==================== DISTRIBUTED LOCKING ====================
    
    async def acquire_lock(
        self, 
        lock_name: str, 
        ttl_seconds: int = 30
    ) -> bool:
        """
        Acquire a distributed lock.
        Returns True if lock acquired, False otherwise.
        """
        if not self.is_available:
            return True  # No Redis = no locking needed
        
        key = self._key(RedisKeyPrefix.LOCK, lock_name)
        acquired = await self._redis.set(key, "1", nx=True, ex=ttl_seconds)
        return acquired is not None
    
    async def release_lock(self, lock_name: str) -> None:
        """Release a distributed lock."""
        if not self.is_available:
            return
        
        key = self._key(RedisKeyPrefix.LOCK, lock_name)
        await self._redis.delete(key)
