"""
Wallet Service
Handles wallet operations: balance, transactions, daily rewards, referrals.
"""
from datetime import datetime, timezone, timedelta

from motor.motor_asyncio import AsyncIOMotorDatabase

from models.schemas import (
    User, WalletTransaction, WalletTransactionResponse,
    TransactionType, TransactionReason
)
from repositories.user_repository import UserRepository
from repositories.wallet_repository import WalletTransactionRepository
from core.exceptions import (
    UserNotFoundError, InsufficientBalanceError, CrickPredictException
)


# Daily reward schedule (streak-based)
DAILY_REWARDS = {
    1: 500,
    2: 600,
    3: 700,
    4: 800,
    5: 900,
    6: 1000,
}
DAILY_REWARD_MAX = 1000
STREAK_BONUS = 200  # Extra for 7+ day streaks


class WalletService:
    """Wallet operations service."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.user_repo = UserRepository(db)
        self.wallet_repo = WalletTransactionRepository(db)
    
    async def get_balance(self, user_id: str) -> dict:
        """Get user's current balance."""
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        
        last_claimed = None
        if user.last_daily_claim:
            ldc = user.last_daily_claim
            last_claimed = ldc.isoformat() if hasattr(ldc, 'isoformat') else str(ldc)
        
        return {
            "user_id": user_id,
            "balance": user.coins_balance,
            "daily_streak": user.daily_streak,
            "can_claim_daily": self._can_claim_daily(user),
            "last_claimed": last_claimed
        }
    
    async def get_transactions(
        self, user_id: str, page: int = 1, limit: int = 20
    ) -> dict:
        """Get paginated transaction history."""
        skip = (page - 1) * limit
        
        transactions = await self.wallet_repo.find_many(
            query={"user_id": user_id},
            sort=[("created_at", -1)],
            skip=skip,
            limit=limit
        )
        
        total = await self.wallet_repo.count({"user_id": user_id})
        
        return {
            "transactions": [
                {
                    "id": t.id,
                    "type": t.type.value if hasattr(t.type, 'value') else t.type,
                    "amount": t.amount,
                    "reason": t.reason.value if hasattr(t.reason, 'value') else t.reason,
                    "balance_after": t.balance_after,
                    "description": t.description,
                    "created_at": t.created_at.isoformat() if hasattr(t.created_at, 'isoformat') else str(t.created_at)
                }
                for t in transactions
            ],
            "page": page,
            "limit": limit,
            "total": total,
            "has_more": (page * limit) < total
        }
    
    def _can_claim_daily(self, user: User) -> bool:
        """Check if user can claim daily reward."""
        if not user.last_daily_claim:
            return True
        
        last_claim = user.last_daily_claim
        if isinstance(last_claim, str):
            last_claim = datetime.fromisoformat(last_claim.replace('Z', '+00:00'))
        
        now = datetime.now(timezone.utc)
        # Can claim if last claim was before today (UTC)
        return last_claim.date() < now.date()
    
    def _calculate_daily_reward(self, streak: int) -> int:
        """Calculate daily reward based on streak."""
        if streak <= 0:
            streak = 1
        
        base = DAILY_REWARDS.get(streak, DAILY_REWARD_MAX)
        bonus = STREAK_BONUS if streak >= 7 else 0
        return base + bonus
    
    def _calculate_streak(self, user: User) -> int:
        """Calculate new streak value."""
        if not user.last_daily_claim:
            return 1
        
        last_claim = user.last_daily_claim
        if isinstance(last_claim, str):
            last_claim = datetime.fromisoformat(last_claim.replace('Z', '+00:00'))
        
        now = datetime.now(timezone.utc)
        days_diff = (now.date() - last_claim.date()).days
        
        if days_diff == 1:
            # Consecutive day - increment streak
            return user.daily_streak + 1
        elif days_diff == 0:
            # Same day - keep streak
            return user.daily_streak
        else:
            # Streak broken - reset to 1
            return 1
    
    async def claim_daily_reward(self, user_id: str) -> dict:
        """Claim daily reward coins."""
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        
        if not self._can_claim_daily(user):
            raise CrickPredictException(
                code="DAILY_ALREADY_CLAIMED",
                message="Daily reward already claimed today. Come back tomorrow!",
                status_code=400
            )
        
        # Calculate streak and reward
        new_streak = self._calculate_streak(user)
        reward_amount = self._calculate_daily_reward(new_streak)
        new_balance = user.coins_balance + reward_amount
        
        # Update user: balance, streak, last_daily_claim, updated_at
        now = datetime.now(timezone.utc)
        await self.user_repo.update_by_id(user_id, {
            "$set": {
                "last_daily_claim": now.isoformat(),
                "daily_streak": new_streak,
                "updated_at": now.isoformat()
            },
            "$inc": {"coins_balance": reward_amount}
        })
        
        # Create transaction record
        await self.wallet_repo.create_transaction(
            user_id=user_id,
            amount=reward_amount,
            transaction_type=TransactionType.CREDIT,
            reason=TransactionReason.DAILY_REWARD,
            balance_after=new_balance,
            description=f"Day {new_streak} daily reward! +{reward_amount} coins"
        )
        
        return {
            "reward_amount": reward_amount,
            "new_balance": new_balance,
            "streak": new_streak,
            "is_streak_bonus": new_streak >= 7,
            "next_reward": self._calculate_daily_reward(new_streak + 1)
        }
