"""
Wallet Router
Handles wallet balance, transactions, and daily rewards.
"""
from fastapi import APIRouter, Depends, Query
from typing import Annotated

from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import get_db
from core.dependencies import CurrentUser
from core.exceptions import CrickPredictException
from models.schemas import User
from services.wallet_service import WalletService


router = APIRouter(prefix="/wallet", tags=["Wallet"])


def get_wallet_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> WalletService:
    return WalletService(db)


@router.get(
    "/balance",
    summary="Get wallet balance",
    description="Get current coin balance and daily reward status"
)
async def get_balance(
    current_user: CurrentUser,
    wallet_service: Annotated[WalletService, Depends(get_wallet_service)]
):
    """Get current wallet balance."""
    return await wallet_service.get_balance(current_user.id)


@router.get(
    "/transactions",
    summary="Transaction history",
    description="Get paginated transaction history"
)
async def get_transactions(
    current_user: CurrentUser,
    wallet_service: Annotated[WalletService, Depends(get_wallet_service)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=50)
):
    """Get transaction history."""
    return await wallet_service.get_transactions(current_user.id, page, limit)


@router.post(
    "/claim-daily",
    summary="Claim daily reward",
    description="Claim daily login reward (streak-based coins)"
)
async def claim_daily_reward(
    current_user: CurrentUser,
    wallet_service: Annotated[WalletService, Depends(get_wallet_service)]
):
    """Claim daily reward."""
    try:
        return await wallet_service.claim_daily_reward(current_user.id)
    except CrickPredictException as e:
        raise e.to_http_exception()
