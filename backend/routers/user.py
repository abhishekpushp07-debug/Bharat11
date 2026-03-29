"""
User Profile Router
Handles user profile, rank, and referral endpoints.
"""
from fastapi import APIRouter, Depends, Query
from typing import Annotated

from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import get_db
from core.dependencies import CurrentUser
from core.exceptions import CrickPredictException
from models.schemas import UserResponse, UserProfileUpdate, User
from services.user_service import UserService


router = APIRouter(prefix="/user", tags=["User Profile"])

PRESET_AVATARS = [
    "/avatars/cricket-bat.svg",
    "/avatars/cricket-ball.svg",
    "/avatars/helmet.svg",
    "/avatars/trophy.svg",
    "/avatars/stadium.svg",
    "/avatars/gloves.svg",
    "/avatars/stumps.svg",
    "/avatars/six.svg",
]


def get_user_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> UserService:
    return UserService(db)


@router.get(
    "/profile",
    response_model=UserResponse,
    summary="Get user profile",
    description="Get current user's profile with stats"
)
async def get_profile(
    current_user: CurrentUser,
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserResponse:
    """Get current user's profile."""
    return await user_service.get_profile(current_user.id)


@router.put(
    "/profile",
    response_model=UserResponse,
    summary="Update profile",
    description="Update username and/or avatar"
)
async def update_profile(
    data: UserProfileUpdate,
    current_user: CurrentUser,
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserResponse:
    """Update user profile."""
    return await user_service.update_profile(current_user.id, data)


@router.get(
    "/rank-progress",
    summary="Get rank progress",
    description="Get user's current rank and progress to next rank"
)
async def get_rank_progress(
    current_user: CurrentUser,
    user_service: Annotated[UserService, Depends(get_user_service)]
):
    """Get rank progress details."""
    return await user_service.get_rank_progress(current_user.id)


@router.get(
    "/referral-stats",
    summary="Get referral stats",
    description="Get referral code and count of referred users"
)
async def get_referral_stats(
    current_user: CurrentUser,
    user_service: Annotated[UserService, Depends(get_user_service)]
):
    """Get referral statistics."""
    return await user_service.get_referral_stats(current_user.id)


@router.get(
    "/avatars",
    summary="Get available avatars",
    description="Get list of preset avatar options"
)
async def get_avatars():
    """Get available preset avatars."""
    return {"avatars": PRESET_AVATARS}


@router.get(
    "/leaderboard",
    summary="Global leaderboard",
    description="Get top players by total points"
)
async def get_leaderboard(
    user_service: Annotated[UserService, Depends(get_user_service)],
    limit: int = Query(default=50, ge=1, le=100)
):
    """Get global leaderboard."""
    return await user_service.get_leaderboard(limit)
