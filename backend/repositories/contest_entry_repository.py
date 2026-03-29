"""
Contest Entry Repository
Handles user entries in contests and predictions.
"""
from typing import Optional, List
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import UpdateOne, ASCENDING, DESCENDING

from repositories.base_repository import BaseRepository
from models.schemas import ContestEntry, Prediction


class ContestEntryRepository(BaseRepository[ContestEntry]):
    """Repository for Contest Entry operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "contest_entries", ContestEntry)
    
    async def find_by_contest_and_user(
        self, 
        contest_id: str, 
        user_id: str
    ) -> Optional[ContestEntry]:
        """Find user's entry in a specific contest."""
        return await self.find_one({
            "contest_id": contest_id,
            "user_id": user_id
        })
    
    async def user_has_joined(
        self, 
        contest_id: str, 
        user_id: str
    ) -> bool:
        """Check if user has already joined a contest."""
        return await self.exists({
            "contest_id": contest_id,
            "user_id": user_id
        })
    
    async def get_user_entries(
        self, 
        user_id: str,
        limit: int = 50
    ) -> List[ContestEntry]:
        """Get all contest entries for a user."""
        return await self.find_many(
            query={"user_id": user_id},
            sort=[("created_at", DESCENDING)],
            limit=limit
        )
    
    async def get_contest_entries(
        self, 
        contest_id: str,
        sort_by_points: bool = True
    ) -> List[ContestEntry]:
        """Get all entries for a contest."""
        sort = [("total_points", DESCENDING)] if sort_by_points else [("created_at", ASCENDING)]
        return await self.find_many(
            query={"contest_id": contest_id},
            sort=sort
        )
    
    async def submit_predictions(
        self,
        contest_id: str,
        user_id: str,
        predictions: List[Prediction]
    ) -> bool:
        """
        Submit or update predictions for a contest entry.
        """
        submission_time = datetime.now(timezone.utc)
        
        # Convert predictions to dict format
        predictions_data = [p.model_dump() for p in predictions]
        
        return await self.update_one(
            query={"contest_id": contest_id, "user_id": user_id},
            update={
                "$set": {
                    "predictions": predictions_data,
                    "submission_time": submission_time.isoformat()
                }
            }
        )
    
    async def update_prediction_result(
        self,
        contest_id: str,
        question_id: str,
        correct_option: str,
        points_per_correct: int
    ) -> int:
        """
        Update all predictions for a question with the correct answer.
        Returns count of correct predictions.
        """
        # Find all entries with this question answered
        entries = await self._collection.find(
            {
                "contest_id": contest_id,
                "predictions.question_id": question_id
            },
            {"_id": 0, "id": 1, "predictions": 1}
        ).to_list(10000)
        
        correct_count = 0
        bulk_ops = []
        
        for entry in entries:
            for pred in entry.get("predictions", []):
                if pred.get("question_id") == question_id:
                    is_correct = pred.get("selected_option") == correct_option
                    points = points_per_correct if is_correct else 0
                    
                    if is_correct:
                        correct_count += 1
                    
                    # Build update operation
                    bulk_ops.append(UpdateOne(
                        {
                            "id": entry["id"],
                            "predictions.question_id": question_id
                        },
                        {
                            "$set": {
                                "predictions.$.is_correct": is_correct,
                                "predictions.$.points_earned": points
                            },
                            "$inc": {"total_points": points}
                        }
                    ))
        
        if bulk_ops:
            await self._collection.bulk_write(bulk_ops)
        
        return correct_count
    
    async def get_leaderboard(
        self,
        contest_id: str,
        limit: int = 50,
        skip: int = 0
    ) -> List[ContestEntry]:
        """
        Get contest leaderboard sorted by points and submission time.
        """
        return await self.find_many(
            query={"contest_id": contest_id},
            sort=[("total_points", DESCENDING), ("submission_time", ASCENDING)],
            skip=skip,
            limit=limit
        )
    
    async def get_user_rank(
        self,
        contest_id: str,
        user_id: str
    ) -> Optional[int]:
        """Get user's rank in a contest leaderboard."""
        entry = await self.find_by_contest_and_user(contest_id, user_id)
        if not entry:
            return None
        
        # Count entries with higher score or same score but earlier submission
        higher_count = await self.count({
            "contest_id": contest_id,
            "$or": [
                {"total_points": {"$gt": entry.total_points}},
                {
                    "total_points": entry.total_points,
                    "submission_time": {"$lt": entry.submission_time.isoformat() if entry.submission_time else ""}
                }
            ]
        })
        
        return higher_count + 1
    
    async def set_final_rank_and_prize(
        self,
        entry_id: str,
        rank: int,
        prize: int
    ) -> bool:
        """Set final rank and prize won for an entry."""
        return await self.update_by_id(
            entry_id,
            {
                "$set": {
                    "final_rank": rank,
                    "prize_won": prize
                }
            }
        )
    
    async def get_entries_for_scoring(
        self,
        contest_id: str,
        question_id: str
    ) -> List[dict]:
        """
        Get entries with their prediction for a specific question.
        Optimized for batch scoring.
        """
        pipeline = [
            {"$match": {"contest_id": contest_id}},
            {"$project": {
                "_id": 0,
                "id": 1,
                "user_id": 1,
                "prediction": {
                    "$filter": {
                        "input": "$predictions",
                        "as": "pred",
                        "cond": {"$eq": ["$$pred.question_id", question_id]}
                    }
                }
            }},
            {"$unwind": {"path": "$prediction", "preserveNullAndEmptyArrays": False}}
        ]
        
        return await self.aggregate(pipeline)
    
    async def count_by_contest(self, contest_id: str) -> int:
        """Get total entries in a contest."""
        return await self.count({"contest_id": contest_id})
