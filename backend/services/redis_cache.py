"""
Bharat 11 - Redis API Response Cache
Ultra-fast caching layer for internal API responses.
Sits between FastAPI routes and MongoDB queries.
TTL-based with automatic invalidation.
"""
import json
import logging
import hashlib
from typing import Optional, Any
from functools import wraps

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

# Global Redis client
_redis: Optional[aioredis.Redis] = None


async def init_redis(url: str = "redis://localhost:6379/0") -> Optional[aioredis.Redis]:
    """Initialize Redis connection. Returns None if Redis unavailable."""
    global _redis
    try:
        _redis = aioredis.from_url(url, decode_responses=True, socket_connect_timeout=2)
        await _redis.ping()
        logger.info("Redis connected successfully")
        return _redis
    except Exception as e:
        logger.warning(f"Redis unavailable (non-critical, falling back to DB): {e}")
        _redis = None
        return None


async def close_redis():
    """Close Redis connection."""
    global _redis
    if _redis:
        await _redis.close()
        _redis = None


def get_redis() -> Optional[aioredis.Redis]:
    """Get Redis client."""
    return _redis


# ==================== TTL CONFIGS ====================
class CacheTTL:
    LIVE_TICKER = 30        # 30s - live scores change rapidly
    POINTS_TABLE = 300      # 5min - changes after each match
    MATCHES_LIST = 60       # 1min - match statuses can change
    MATCH_INFO = 120        # 2min - live match info
    CONTESTS_LIST = 60      # 1min
    USER_CONTESTS = 30      # 30s - user's contest data
    HOT_CONTESTS = 60       # 1min
    IPL_PLAYERS = 600       # 10min - static data
    IPL_RECORDS = 600       # 10min - static data
    IPL_CAPS = 600          # 10min - static data
    ADMIN_STATS = 30        # 30s - admin dashboard


# ==================== CORE CACHE OPERATIONS ====================
async def cache_get(key: str) -> Optional[Any]:
    """Get value from Redis cache."""
    if not _redis:
        return None
    try:
        val = await _redis.get(f"b11:{key}")
        return json.loads(val) if val else None
    except Exception:
        return None


async def cache_set(key: str, value: Any, ttl: int = 60) -> bool:
    """Set value in Redis cache with TTL."""
    if not _redis:
        return False
    try:
        await _redis.setex(f"b11:{key}", ttl, json.dumps(value, default=str))
        return True
    except Exception:
        return False


async def cache_delete(pattern: str):
    """Delete cache keys matching pattern."""
    if not _redis:
        return
    try:
        keys = []
        async for key in _redis.scan_iter(f"b11:{pattern}*"):
            keys.append(key)
        if keys:
            await _redis.delete(*keys)
    except Exception:
        pass


async def cache_invalidate_match(match_id: str = ""):
    """Invalidate all match-related caches."""
    await cache_delete("matches:")
    if match_id:
        await cache_delete(f"match:{match_id}")
    await cache_delete("contests:")
    await cache_delete("hot_contests")


async def cache_invalidate_contest(contest_id: str = ""):
    """Invalidate all contest-related caches."""
    await cache_delete("contests:")
    await cache_delete("user_contests:")
    await cache_delete("hot_contests")
    if contest_id:
        await cache_delete(f"contest:{contest_id}")


async def get_cache_stats() -> dict:
    """Get Redis cache statistics."""
    if not _redis:
        return {"status": "disconnected", "keys": 0}
    try:
        info = await _redis.info("memory")
        keys = await _redis.dbsize()
        return {
            "status": "connected",
            "keys": keys,
            "memory_used": info.get("used_memory_human", "?"),
            "memory_peak": info.get("used_memory_peak_human", "?"),
        }
    except Exception as e:
        return {"status": f"error: {e}", "keys": 0}
