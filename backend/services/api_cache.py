"""
Bharat 11 - MongoDB API Cache Layer
Stores all CricketData.org API responses in MongoDB to prevent duplicate API calls.
Strategy:
- Completed match data: cached permanently (never re-fetched)
- Live match data: cached with short TTL (re-fetched when stale)
- Series data: cached with long TTL (schedule/squads don't change often)
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Any

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

# TTL configs (in seconds)
TTL_PERMANENT = 0  # Never expires
TTL_LIVE_SCORE = 45  # Re-fetch every 45s for live matches
TTL_SERIES_INFO = 86400  # 24 hours
TTL_SERIES_SQUAD = 86400  # 24 hours
TTL_SERIES_POINTS = 1800  # 30 min
TTL_MATCH_INFO = 3600  # 1 hour (or permanent if completed)
TTL_SCORECARD = 45  # 45s for live (match polling interval)
TTL_MATCH_POINTS = 300  # 5 min (slow API)
TTL_MATCH_SQUAD = 86400  # 24 hours (doesn't change)
TTL_MATCH_BBB = 60  # 1 min for live
TTL_PLAYER_INFO = 86400  # 24 hours
TTL_CRIC_SCORE = 45  # 45 seconds


async def get_cached(db: AsyncIOMotorDatabase, cache_type: str, cache_key: str, ttl: int = 0) -> Optional[dict]:
    """
    Get data from api_cache collection.
    Returns None if not found or expired.
    ttl=0 means permanent cache (never expires).
    """
    doc = await db.api_cache.find_one(
        {"cache_type": cache_type, "cache_key": cache_key},
        {"_id": 0}
    )
    if not doc:
        return None

    # Permanent cache
    if ttl == 0 or doc.get("permanent", False):
        return doc.get("data")

    # Check TTL
    cached_at = doc.get("cached_at")
    if cached_at:
        if isinstance(cached_at, str):
            cached_at = datetime.fromisoformat(cached_at.replace('Z', '+00:00'))
        # Ensure timezone-aware
        if cached_at.tzinfo is None:
            cached_at = cached_at.replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - cached_at).total_seconds()
        if age < ttl:
            return doc.get("data")

    return None


async def set_cache(db: AsyncIOMotorDatabase, cache_type: str, cache_key: str, data: Any, permanent: bool = False):
    """Store API response in MongoDB cache."""
    now = datetime.now(timezone.utc)
    await db.api_cache.update_one(
        {"cache_type": cache_type, "cache_key": cache_key},
        {"$set": {
            "cache_type": cache_type,
            "cache_key": cache_key,
            "data": data,
            "permanent": permanent,
            "cached_at": now,
            "updated_at": now,
        }},
        upsert=True,
    )


async def is_match_completed(db: AsyncIOMotorDatabase, match_id: str) -> bool:
    """Check if a match is completed (from our matches collection or from cached data)."""
    match = await db.matches.find_one(
        {"$or": [{"id": match_id}, {"cricketdata_id": match_id}, {"external_match_id": match_id}]},
        {"_id": 0, "status": 1}
    )
    if match and match.get("status") == "completed":
        return True
    # Also check cached match_info
    cached = await db.api_cache.find_one(
        {"cache_type": "match_info", "cache_key": match_id},
        {"_id": 0, "data.matchEnded": 1}
    )
    if cached and cached.get("data", {}).get("matchEnded"):
        return True
    return False


class CachedCricketService:
    """
    Wraps UnifiedCricketService with MongoDB persistence.
    Check DB first -> if miss, call API -> store in DB.
    """

    def __init__(self):
        from services.cricket_data import cricket_service
        self.api = cricket_service

    async def get_series_info(self, db: AsyncIOMotorDatabase, series_id: str) -> Optional[dict]:
        cached = await get_cached(db, "series_info", series_id, TTL_SERIES_INFO)
        if cached:
            logger.debug(f"Cache HIT: series_info/{series_id}")
            return cached
        data = await self.api.get_series_info(series_id)
        if data:
            await set_cache(db, "series_info", series_id, data, permanent=False)
        return data

    async def get_series_points(self, db: AsyncIOMotorDatabase, series_id: str) -> Optional[list]:
        cached = await get_cached(db, "series_points", series_id, TTL_SERIES_POINTS)
        if cached:
            logger.debug(f"Cache HIT: series_points/{series_id}")
            return cached
        data = await self.api.get_series_points(series_id)
        if data:
            await set_cache(db, "series_points", series_id, data)
        return data

    async def get_series_squad(self, db: AsyncIOMotorDatabase, series_id: str) -> Optional[list]:
        cached = await get_cached(db, "series_squad", series_id, TTL_SERIES_SQUAD)
        if cached:
            logger.debug(f"Cache HIT: series_squad/{series_id}")
            return cached
        data = await self.api.get_series_squad(series_id)
        if data:
            await set_cache(db, "series_squad", series_id, data, permanent=True)
        return data

    async def get_match_info(self, db: AsyncIOMotorDatabase, match_id: str) -> Optional[dict]:
        completed = await is_match_completed(db, match_id)
        ttl = TTL_PERMANENT if completed else TTL_MATCH_INFO
        cached = await get_cached(db, "match_info", match_id, ttl)
        if cached:
            logger.debug(f"Cache HIT: match_info/{match_id}")
            return cached
        data = await self.api.get_match_info(match_id)
        if data:
            is_ended = data.get("matchEnded", False)
            await set_cache(db, "match_info", match_id, data, permanent=is_ended)
        return data

    async def get_scorecard(self, db: AsyncIOMotorDatabase, match_id: str) -> Optional[dict]:
        completed = await is_match_completed(db, match_id)
        ttl = TTL_PERMANENT if completed else TTL_SCORECARD
        cached = await get_cached(db, "scorecard", match_id, ttl)
        if cached:
            logger.debug(f"Cache HIT: scorecard/{match_id}")
            return cached
        data = await self.api.get_scorecard(match_id)
        if data:
            is_ended = data.get("matchEnded", False)
            await set_cache(db, "scorecard", match_id, data, permanent=is_ended)
        return data

    async def get_match_points(self, db: AsyncIOMotorDatabase, match_id: str) -> Optional[dict]:
        completed = await is_match_completed(db, match_id)
        ttl = TTL_PERMANENT if completed else TTL_MATCH_POINTS
        cached = await get_cached(db, "match_points", match_id, ttl)
        if cached:
            logger.debug(f"Cache HIT: match_points/{match_id}")
            return cached
        data = await self.api.get_match_points(match_id)
        if data:
            await set_cache(db, "match_points", match_id, data, permanent=completed)
        return data

    async def get_squad(self, db: AsyncIOMotorDatabase, match_id: str) -> Optional[dict]:
        cached = await get_cached(db, "match_squad", match_id, TTL_MATCH_SQUAD)
        if cached:
            logger.debug(f"Cache HIT: match_squad/{match_id}")
            return cached
        data = await self.api.get_squad(match_id)
        if data:
            await set_cache(db, "match_squad", match_id, data, permanent=True)
        return data

    async def get_match_bbb(self, db: AsyncIOMotorDatabase, match_id: str) -> Optional[dict]:
        completed = await is_match_completed(db, match_id)
        ttl = TTL_PERMANENT if completed else TTL_MATCH_BBB
        cached = await get_cached(db, "match_bbb", match_id, ttl)
        if cached:
            logger.debug(f"Cache HIT: match_bbb/{match_id}")
            return cached
        data = await self.api.get_match_bbb(match_id)
        if data:
            await set_cache(db, "match_bbb", match_id, data, permanent=completed)
        return data

    async def get_player_info(self, db: AsyncIOMotorDatabase, player_id: str) -> Optional[dict]:
        cached = await get_cached(db, "player_info", player_id, TTL_PLAYER_INFO)
        if cached:
            logger.debug(f"Cache HIT: player_info/{player_id}")
            return cached
        data = await self.api.get_player_info(player_id)
        if data:
            await set_cache(db, "player_info", player_id, data, permanent=True)
        return data

    async def get_cric_score(self, db: AsyncIOMotorDatabase) -> Optional[list]:
        cached = await get_cached(db, "cric_score", "all", TTL_CRIC_SCORE)
        if cached:
            logger.debug("Cache HIT: cric_score/all")
            return cached
        data = await self.api.get_cric_score()
        if data:
            await set_cache(db, "cric_score", "all", data)
        return data

    async def get_cache_stats(self, db: AsyncIOMotorDatabase) -> dict:
        """Get cache statistics."""
        total = await db.api_cache.count_documents({})
        permanent = await db.api_cache.count_documents({"permanent": True})
        by_type = await db.api_cache.aggregate([
            {"$group": {"_id": "$cache_type", "count": {"$sum": 1}}}
        ]).to_list(50)
        return {
            "total_cached": total,
            "permanent_cached": permanent,
            "by_type": {r["_id"]: r["count"] for r in by_type},
        }


# Singleton
cached_cricket = CachedCricketService()
