"""
User Repository
Handles all user-related database operations.
"""
from typing import Optional, List
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import UpdateOne

from repositories.base_repository import BaseRepository
from models.schemas import User, UserRank
from core.exceptions import UserNotFoundError, UserAlreadyExistsError


class UserRepository(BaseRepository[User]):
    """Repository for User collection operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "users", User)
    
    async def find_by_phone(self, phone: str) -> Optional[User]:
        """Find user by phone number."""
        # Clean phone number
        cleaned_phone = ''.join(c for c in phone if c.isdigit())
        return await self.find_one({"phone": cleaned_phone})
    
    async def find_by_referral_code(self, code: str) -> Optional[User]:
        """Find user by their referral code."""
        return await self.find_one({"referral_code": code.upper()})
    
    async def phone_exists(self, phone: str) -> bool:
        """Check if phone number is already registered."""
        cleaned_phone = ''.join(c for c in phone if c.isdigit())
        return await self.exists({"phone": cleaned_phone})
    
    async def create_user(self, user: User) -> User:
        """
        Create a new user with uniqueness check.
        Raises UserAlreadyExistsError if phone exists.
        """
        if await self.phone_exists(user.phone):
            raise UserAlreadyExistsError(user.phone)
        
        return await self.create(user)
    
    async def update_coins(
        self, 
        user_id: str, 
        amount: int, 
        operation: str = "add"
    ) -> bool:
        """
        Update user's coin balance with atomic safety.
        For subtract: uses $gte guard to prevent negative balance.
        
        Returns:
            True if updated, False if insufficient balance (subtract only)
        """
        if operation == "subtract":
            # Atomic: only subtract if balance >= amount (prevents negative)
            result = await self._collection.update_one(
                {"id": user_id, "coins_balance": {"$gte": amount}},
                {"$inc": {"coins_balance": -amount}}
            )
            return result.modified_count > 0
        
        return await self.update_by_id(
            user_id,
            {"$inc": {"coins_balance": amount}}
        )
    
    async def update_stats(
        self,
        user_id: str,
        points: int = 0,
        matches: int = 0,
        wins: int = 0
    ) -> bool:
        """
        Update user statistics after a contest.
        Also recalculates rank title.
        """
        # First, increment stats
        update = {
            "$inc": {
                "total_points": points,
                "matches_played": matches,
                "contests_won": wins
            }
        }
        
        result = await self.update_by_id(user_id, update)
        
        if result and points > 0:
            # Fetch updated user to recalculate rank
            user = await self.find_by_id(user_id)
            if user:
                new_rank = user.calculate_rank()
                if new_rank != user.rank_title:
                    await self.update_by_id(
                        user_id,
                        {"$set": {"rank_title": new_rank.value}}
                    )
        
        return result
    
    async def update_daily_streak(
        self,
        user_id: str,
        new_streak: int,
        claim_time: datetime
    ) -> bool:
        """Update daily streak and last claim time."""
        return await self.update_by_id(
            user_id,
            {
                "$set": {
                    "daily_streak": new_streak,
                    "last_daily_claim": claim_time.isoformat()
                }
            }
        )
    
    async def increment_failed_login(self, user_id: str) -> int:
        """
        Increment failed login attempts.
        Returns new count.
        """
        result = await self._collection.find_one_and_update(
            {"id": user_id},
            {"$inc": {"failed_login_attempts": 1}},
            return_document=True,
            projection={"_id": 0, "failed_login_attempts": 1}
        )
        return result.get("failed_login_attempts", 0) if result else 0
    
    async def reset_failed_login(self, user_id: str) -> bool:
        """Reset failed login attempts after successful login."""
        return await self.update_by_id(
            user_id,
            {"$set": {"failed_login_attempts": 0, "locked_until": None}}
        )
    
    async def lock_account(self, user_id: str, until: datetime) -> bool:
        """Lock user account until specified time."""
        return await self.update_by_id(
            user_id,
            {"$set": {"locked_until": until.isoformat()}}
        )
    
    async def get_leaderboard(self, limit: int = 100) -> List[User]:
        """Get top users by total points."""
        return await self.find_many(
            query={},
            sort=[("total_points", -1)],
            limit=limit,
            projection={
                "id": 1,
                "username": 1,
                "avatar_url": 1,
                "total_points": 1,
                "rank_title": 1,
                "contests_won": 1
            }
        )
    
    async def get_referral_count(self, user_id: str) -> int:
        """Get count of users referred by this user."""
        return await self.count({"referred_by": user_id})
    
    async def search_users(
        self,
        query: str,
        limit: int = 20
    ) -> List[User]:
        """Search users by username or phone (partial match)."""
        search_query = {
            "$or": [
                {"username": {"$regex": query, "$options": "i"}},
                {"phone": {"$regex": query}}
            ]
        }
        return await self.find_many(
            query=search_query,
            limit=limit,
            projection={
                "id": 1,
                "username": 1,
                "avatar_url": 1,
                "rank_title": 1
            }
        )
