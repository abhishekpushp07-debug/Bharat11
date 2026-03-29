"""
Question Result Repository
Handles resolved question results for matches.
"""
from typing import Optional, List

from motor.motor_asyncio import AsyncIOMotorDatabase

from repositories.base_repository import BaseRepository
from models.schemas import QuestionResult


class QuestionResultRepository(BaseRepository[QuestionResult]):
    """Repository for Question Result operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "question_results", QuestionResult)
    
    async def find_by_match_and_question(
        self,
        match_id: str,
        question_id: str
    ) -> Optional[QuestionResult]:
        """Find result for a specific question in a match."""
        return await self.find_one({
            "match_id": match_id,
            "question_id": question_id
        })
    
    async def is_resolved(
        self,
        match_id: str,
        question_id: str
    ) -> bool:
        """Check if a question has been resolved for a match."""
        return await self.exists({
            "match_id": match_id,
            "question_id": question_id
        })
    
    async def get_match_results(
        self,
        match_id: str
    ) -> List[QuestionResult]:
        """Get all resolved question results for a match."""
        return await self.find_many(
            query={"match_id": match_id},
            sort=[("resolved_at", 1)]
        )
    
    async def get_resolved_count(self, match_id: str) -> int:
        """Get count of resolved questions for a match."""
        return await self.count({"match_id": match_id})
    
    async def store_result(
        self,
        match_id: str,
        question_id: str,
        correct_option: str,
        resolution_data: dict
    ) -> QuestionResult:
        """
        Store a question result.
        Uses upsert to prevent duplicates.
        """
        result = QuestionResult(
            match_id=match_id,
            question_id=question_id,
            correct_option=correct_option,
            resolution_data=resolution_data
        )
        
        # Upsert to prevent duplicate results
        await self._collection.update_one(
            {"match_id": match_id, "question_id": question_id},
            {"$set": self._to_document(result)},
            upsert=True
        )
        
        return result
    
    async def get_results_map(
        self,
        match_id: str
    ) -> dict:
        """
        Get question results as a map {question_id: correct_option}.
        Useful for quick lookups during leaderboard display.
        """
        results = await self.get_match_results(match_id)
        return {r.question_id: r.correct_option for r in results}
