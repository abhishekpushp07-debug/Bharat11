"""
Contest Repository
Handles all contest-related database operations.
"""
from typing import Optional, List
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import UpdateOne

from repositories.base_repository import BaseRepository
from models.schemas import Contest, ContestStatus


class ContestRepository(BaseRepository[Contest]):
    """Repository for Contest collection operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "contests", Contest)
    
    async def get_by_match(
        self, 
        match_id: str,
        status: Optional[ContestStatus] = None
    ) -> List[Contest]:
        """Get all contests for a match, optionally filtered by status."""
        query = {"match_id": match_id}
        if status:
            query["status"] = status.value
        
        return await self.find_many(
            query=query,
            sort=[("entry_fee", 1)]  # Sort by entry fee (free first)
        )
    
    async def get_open_contests(self, match_id: str) -> List[Contest]:
        """Get contests that are still open for joining."""
        return await self.find_many(
            query={
                "match_id": match_id,
                "status": ContestStatus.OPEN.value,
                "lock_time": {"$gt": datetime.now(timezone.utc).isoformat()}
            },
            sort=[("entry_fee", 1)]
        )
    
    async def get_live_contests(self, match_id: str) -> List[Contest]:
        """Get currently live contests for a match."""
        return await self.find_many(
            query={
                "match_id": match_id,
                "status": ContestStatus.LIVE.value
            }
        )
    
    async def increment_participants(self, contest_id: str) -> bool:
        """Increment participant count when a user joins."""
        result = await self._collection.find_one_and_update(
            {
                "id": contest_id,
                "$expr": {"$lt": ["$current_participants", "$max_participants"]}
            },
            {"$inc": {"current_participants": 1}},
            return_document=True,
            projection={"_id": 0, "current_participants": 1}
        )
        return result is not None
    
    async def decrement_participants(self, contest_id: str) -> bool:
        """Decrement participant count if user leaves (before lock)."""
        return await self.update_by_id(
            contest_id,
            {"$inc": {"current_participants": -1}}
        )
    
    async def update_status(
        self, 
        contest_id: str, 
        status: ContestStatus
    ) -> bool:
        """Update contest status."""
        return await self.update_by_id(
            contest_id,
            {"$set": {"status": status.value}}
        )
    
    async def lock_contest(self, contest_id: str) -> bool:
        """Lock a contest (no more entries allowed)."""
        return await self.update_status(contest_id, ContestStatus.LOCKED)
    
    async def start_contest(self, contest_id: str) -> bool:
        """Start a contest (match has begun)."""
        return await self.update_status(contest_id, ContestStatus.LIVE)
    
    async def complete_contest(self, contest_id: str) -> bool:
        """Mark contest as completed."""
        return await self.update_status(contest_id, ContestStatus.COMPLETED)
    
    async def cancel_contest(self, contest_id: str) -> bool:
        """Cancel a contest."""
        return await self.update_status(contest_id, ContestStatus.CANCELLED)
    
    async def is_full(self, contest_id: str) -> bool:
        """Check if contest has reached max participants."""
        contest = await self.find_by_id(
            contest_id,
            projection={"current_participants": 1, "max_participants": 1}
        )
        if not contest:
            return True  # Treat not found as full
        return contest.current_participants >= contest.max_participants
    
    async def is_joinable(self, contest_id: str) -> bool:
        """Check if contest can be joined (open, not full, not locked)."""
        now = datetime.now(timezone.utc).isoformat()
        doc = await self._collection.find_one(
            {
                "id": contest_id,
                "status": ContestStatus.OPEN.value,
                "lock_time": {"$gt": now},
                "$expr": {"$lt": ["$current_participants", "$max_participants"]}
            },
            {"_id": 1}
        )
        return doc is not None
    
    async def get_contests_to_lock(self) -> List[Contest]:
        """Get contests that should be locked (lock_time has passed)."""
        now = datetime.now(timezone.utc).isoformat()
        return await self.find_many(
            query={
                "status": ContestStatus.OPEN.value,
                "lock_time": {"$lte": now}
            }
        )
    
    async def bulk_update_status(
        self, 
        contest_ids: List[str], 
        status: ContestStatus
    ) -> int:
        """Update status for multiple contests."""
        if not contest_ids:
            return 0
        
        result = await self._collection.update_many(
            {"id": {"$in": contest_ids}},
            {"$set": {"status": status.value}}
        )
        return result.modified_count
    
    async def get_user_active_contests(
        self,
        user_id: str,
        entry_collection
    ) -> List[Contest]:
        """
        Get contests where user has an active entry.
        Requires passing contest_entries collection.
        """
        # Get user's contest entries
        entries = await entry_collection.find(
            {"user_id": user_id},
            {"contest_id": 1}
        ).to_list(100)
        
        contest_ids = [e["contest_id"] for e in entries]
        
        if not contest_ids:
            return []
        
        return await self.find_many(
            query={
                "id": {"$in": contest_ids},
                "status": {"$in": [
                    ContestStatus.OPEN.value,
                    ContestStatus.LOCKED.value,
                    ContestStatus.LIVE.value
                ]}
            },
            sort=[("lock_time", 1)]
        )
