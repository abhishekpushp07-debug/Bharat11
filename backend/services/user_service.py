"""
User Service
Handles user profile operations, rank calculation, and referral system.
"""
from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from models.schemas import User, UserResponse, UserProfileUpdate, UserRank
from repositories.user_repository import UserRepository
from core.exceptions import UserNotFoundError, InvalidReferralCodeError


class UserService:
    """User profile and rank management service."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def _user_to_response(self, user: User) -> UserResponse:
        """Convert User model to response DTO."""
        return UserResponse(
            id=user.id,
            phone=user.phone,
            username=user.username,
            avatar_url=user.avatar_url,
            coins_balance=user.coins_balance,
            rank_title=user.rank_title,
            total_points=user.total_points,
            matches_played=user.matches_played,
            contests_won=user.contests_won,
            referral_code=user.referral_code,
            daily_streak=user.daily_streak,
            created_at=user.created_at
        )
    
    async def get_profile(self, user_id: str) -> UserResponse:
        """Get user profile."""
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return self._user_to_response(user)
    
    async def update_profile(
        self, user_id: str, update_data: UserProfileUpdate
    ) -> UserResponse:
        """Update user profile (username, avatar) with updated_at."""
        update_fields = {}
        if update_data.username is not None:
            # Validate username
            if len(update_data.username.strip()) < 3:
                from core.exceptions import ValidationError
                raise ValidationError("Username must be at least 3 characters")
            if len(update_data.username) > 20:
                from core.exceptions import ValidationError
                raise ValidationError("Username must be 20 characters or less")
            update_fields["username"] = update_data.username.strip()
        if update_data.avatar_url is not None:
            update_fields["avatar_url"] = update_data.avatar_url
        
        if update_fields:
            update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
            await self.user_repo.update_by_id(user_id, {"$set": update_fields})
        
        return await self.get_profile(user_id)
    
    async def get_rank_progress(self, user_id: str) -> dict:
        """Get user's rank and progress to next rank."""
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        
        rank_thresholds = [
            (UserRank.ROOKIE, 0, 999),
            (UserRank.PRO, 1000, 4999),
            (UserRank.EXPERT, 5000, 14999),
            (UserRank.LEGEND, 15000, 49999),
            (UserRank.GOAT, 50000, 999999),
        ]
        
        current_rank = user.calculate_rank()
        points = user.total_points
        
        # Find current tier
        for rank, low, high in rank_thresholds:
            if rank == current_rank:
                progress = ((points - low) / (high - low + 1)) * 100 if high > low else 100
                next_rank = None
                points_to_next = 0
                idx = rank_thresholds.index((rank, low, high))
                if idx < len(rank_thresholds) - 1:
                    next_rank = rank_thresholds[idx + 1][0].value
                    points_to_next = rank_thresholds[idx + 1][1] - points
                
                return {
                    "current_rank": current_rank.value,
                    "total_points": points,
                    "rank_min": low,
                    "rank_max": high,
                    "progress_percent": min(round(progress, 1), 100),
                    "next_rank": next_rank,
                    "points_to_next": max(points_to_next, 0)
                }
        
        return {"current_rank": current_rank.value, "total_points": points}
    
    async def get_referral_stats(self, user_id: str) -> dict:
        """Get referral statistics for a user."""
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        
        # Count referred users
        referred_count = await self.user_repo.count({"referred_by": user_id})
        
        return {
            "referral_code": user.referral_code,
            "total_referrals": referred_count,
            "bonus_per_referral": 1000
        }
    
    async def get_leaderboard(self, limit: int = 50) -> list:
        """Get global leaderboard."""
        # Use raw query with projection (avoids User model validation for partial data)
        cursor = self.db.users.find(
            {},
            {
                "_id": 0,
                "id": 1,
                "username": 1,
                "avatar_url": 1,
                "total_points": 1,
                "rank_title": 1,
                "matches_played": 1,
                "contests_won": 1
            }
        ).sort("total_points", -1).limit(limit)
        
        users = await cursor.to_list(length=limit)
        return [
            {
                "rank": idx + 1,
                "user_id": u.get("id", ""),
                "username": u.get("username", ""),
                "total_points": u.get("total_points", 0),
                "rank_title": u.get("rank_title", "Rookie"),
                "avatar_url": u.get("avatar_url"),
                "matches_played": u.get("matches_played", 0),
                "contests_won": u.get("contests_won", 0)
            }
            for idx, u in enumerate(users)
        ]
