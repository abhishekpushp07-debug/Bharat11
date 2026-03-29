"""
Match Repository
Handles all match-related database operations.
"""
from typing import Optional, List
from datetime import datetime, timezone, timedelta

from motor.motor_asyncio import AsyncIOMotorDatabase

from repositories.base_repository import BaseRepository
from models.schemas import Match, MatchStatus, MatchType


class MatchRepository(BaseRepository[Match]):
    """Repository for Match collection operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "matches", Match)
    
    async def find_by_external_id(self, external_id: str) -> Optional[Match]:
        """Find match by external (Cricbuzz) ID."""
        return await self.find_one({"external_match_id": external_id})
    
    async def get_upcoming_matches(self, limit: int = 20) -> List[Match]:
        """Get upcoming matches sorted by start time."""
        return await self.find_many(
            query={"status": MatchStatus.UPCOMING.value},
            sort=[("start_time", 1)],
            limit=limit
        )
    
    async def get_live_matches(self) -> List[Match]:
        """Get all currently live matches."""
        return await self.find_many(
            query={"status": MatchStatus.LIVE.value},
            sort=[("start_time", 1)]
        )
    
    async def get_completed_matches(
        self, 
        limit: int = 20,
        days_back: int = 7
    ) -> List[Match]:
        """Get recently completed matches."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
        return await self.find_many(
            query={
                "status": MatchStatus.COMPLETED.value,
                "start_time": {"$gte": cutoff.isoformat()}
            },
            sort=[("start_time", -1)],
            limit=limit
        )
    
    async def get_matches_by_status(
        self, 
        status: MatchStatus,
        limit: int = 50
    ) -> List[Match]:
        """Get matches filtered by status."""
        sort_order = 1 if status == MatchStatus.UPCOMING else -1
        return await self.find_many(
            query={"status": status.value},
            sort=[("start_time", sort_order)],
            limit=limit
        )
    
    async def update_status(
        self, 
        match_id: str, 
        status: MatchStatus
    ) -> bool:
        """Update match status."""
        return await self.update_by_id(
            match_id,
            {"$set": {"status": status.value}}
        )
    
    async def update_live_score(
        self, 
        match_id: str, 
        live_score: dict
    ) -> bool:
        """Update live score data for a match."""
        return await self.update_by_id(
            match_id,
            {"$set": {"live_score": live_score, "status": MatchStatus.LIVE.value}}
        )
    
    async def set_result(
        self, 
        match_id: str, 
        result: str
    ) -> bool:
        """Set match result and mark as completed."""
        return await self.update_by_id(
            match_id,
            {
                "$set": {
                    "result": result,
                    "status": MatchStatus.COMPLETED.value
                }
            }
        )
    
    async def assign_templates(
        self, 
        match_id: str, 
        template_ids: List[str]
    ) -> bool:
        """Assign question templates to a match."""
        return await self.update_by_id(
            match_id,
            {"$set": {"templates_assigned": template_ids}}
        )
    
    async def get_matches_starting_soon(
        self, 
        minutes: int = 30
    ) -> List[Match]:
        """Get matches starting within specified minutes."""
        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(minutes=minutes)
        
        return await self.find_many(
            query={
                "status": MatchStatus.UPCOMING.value,
                "start_time": {
                    "$gte": now.isoformat(),
                    "$lte": cutoff.isoformat()
                }
            },
            sort=[("start_time", 1)]
        )
    
    async def get_matches_needing_lock(
        self, 
        lock_before_minutes: int = 15
    ) -> List[Match]:
        """
        Get upcoming matches that need to have their contests locked.
        These are matches starting within lock_before_minutes.
        """
        now = datetime.now(timezone.utc)
        lock_time = now + timedelta(minutes=lock_before_minutes)
        
        return await self.find_many(
            query={
                "status": MatchStatus.UPCOMING.value,
                "start_time": {"$lte": lock_time.isoformat()}
            }
        )
    
    async def search_matches(
        self,
        query: str,
        limit: int = 20
    ) -> List[Match]:
        """Search matches by team name or venue."""
        search_query = {
            "$or": [
                {"team_a.name": {"$regex": query, "$options": "i"}},
                {"team_b.name": {"$regex": query, "$options": "i"}},
                {"team_a.short_name": {"$regex": query, "$options": "i"}},
                {"team_b.short_name": {"$regex": query, "$options": "i"}},
                {"venue": {"$regex": query, "$options": "i"}}
            ]
        }
        return await self.find_many(
            query=search_query,
            sort=[("start_time", -1)],
            limit=limit
        )
