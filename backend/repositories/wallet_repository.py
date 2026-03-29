"""
Wallet Repository
Handles wallet transactions and balance operations.
"""
from typing import Optional, List
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING, ASCENDING

from repositories.base_repository import BaseRepository
from models.schemas import WalletTransaction, TransactionType, TransactionReason


class WalletTransactionRepository(BaseRepository[WalletTransaction]):
    """Repository for Wallet Transaction operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "wallet_transactions", WalletTransaction)
    
    async def get_user_transactions(
        self,
        user_id: str,
        limit: int = 20,
        skip: int = 0,
        transaction_type: Optional[TransactionType] = None
    ) -> List[WalletTransaction]:
        """Get user's transaction history."""
        query = {"user_id": user_id}
        if transaction_type:
            query["type"] = transaction_type.value
        
        return await self.find_many(
            query=query,
            sort=[("created_at", DESCENDING)],
            skip=skip,
            limit=limit
        )
    
    async def get_by_reference(
        self,
        user_id: str,
        reference_id: str,
        reason: TransactionReason
    ) -> Optional[WalletTransaction]:
        """Find transaction by reference (e.g., contest_id)."""
        return await self.find_one({
            "user_id": user_id,
            "reference_id": reference_id,
            "reason": reason.value
        })
    
    async def create_transaction(
        self,
        user_id: str,
        amount: int,
        transaction_type: TransactionType,
        reason: TransactionReason,
        balance_after: int,
        reference_id: Optional[str] = None,
        description: Optional[str] = None
    ) -> WalletTransaction:
        """Create a new wallet transaction."""
        transaction = WalletTransaction(
            user_id=user_id,
            type=transaction_type,
            amount=amount,
            reason=reason,
            reference_id=reference_id,
            balance_after=balance_after,
            description=description
        )
        return await self.create(transaction)
    
    async def get_total_earned(
        self,
        user_id: str,
        reason: Optional[TransactionReason] = None
    ) -> int:
        """Get total amount earned (credited) by a user."""
        query = {
            "user_id": user_id,
            "type": TransactionType.CREDIT.value
        }
        if reason:
            query["reason"] = reason.value
        
        pipeline = [
            {"$match": query},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        
        result = await self.aggregate(pipeline, limit=1)
        return result[0]["total"] if result else 0
    
    async def get_total_spent(
        self,
        user_id: str,
        reason: Optional[TransactionReason] = None
    ) -> int:
        """Get total amount spent (debited) by a user."""
        query = {
            "user_id": user_id,
            "type": TransactionType.DEBIT.value
        }
        if reason:
            query["reason"] = reason.value
        
        pipeline = [
            {"$match": query},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        
        result = await self.aggregate(pipeline, limit=1)
        return result[0]["total"] if result else 0
    
    async def has_claimed_daily_today(self, user_id: str) -> bool:
        """Check if user has claimed daily reward today."""
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        
        return await self.exists({
            "user_id": user_id,
            "reason": TransactionReason.DAILY_REWARD.value,
            "created_at": {"$gte": today_start.isoformat()}
        })
    
    async def get_contest_transactions(
        self,
        user_id: str,
        contest_id: str
    ) -> List[WalletTransaction]:
        """Get all transactions related to a contest for a user."""
        return await self.find_many(
            query={
                "user_id": user_id,
                "reference_id": contest_id,
                "reason": {"$in": [
                    TransactionReason.CONTEST_ENTRY.value,
                    TransactionReason.CONTEST_WIN.value,
                    TransactionReason.REFUND.value
                ]}
            },
            sort=[("created_at", ASCENDING)]
        )
    
    async def get_daily_summary(
        self,
        user_id: str,
        days: int = 7
    ) -> List[dict]:
        """Get daily transaction summary for the last N days."""
        cutoff = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        
        from datetime import timedelta
        start_date = cutoff - timedelta(days=days)
        
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "created_at": {"$gte": start_date.isoformat()}
                }
            },
            {
                "$group": {
                    "_id": {
                        "date": {"$substr": ["$created_at", 0, 10]},
                        "type": "$type"
                    },
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id.date": DESCENDING}}
        ]
        
        return await self.aggregate(pipeline)
