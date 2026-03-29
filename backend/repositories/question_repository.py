"""
Question Repository
Handles question bank and template operations.
"""
from typing import Optional, List

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING

from repositories.base_repository import BaseRepository
from models.schemas import Question, Template, QuestionCategory, QuestionDifficulty


class QuestionRepository(BaseRepository[Question]):
    """Repository for Question Bank operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "questions", Question)
    
    async def get_active_questions(
        self,
        category: Optional[QuestionCategory] = None,
        difficulty: Optional[QuestionDifficulty] = None,
        limit: int = 100
    ) -> List[Question]:
        """Get active questions with optional filters."""
        query = {"is_active": True}
        
        if category:
            query["category"] = category.value
        if difficulty:
            query["difficulty"] = difficulty.value
        
        return await self.find_many(
            query=query,
            sort=[("category", ASCENDING), ("points", ASCENDING)],
            limit=limit
        )
    
    async def get_by_ids(self, question_ids: List[str]) -> List[Question]:
        """Get multiple questions by their IDs."""
        return await self.find_many(
            query={"id": {"$in": question_ids}},
            limit=len(question_ids)
        )
    
    async def get_by_category(
        self,
        category: QuestionCategory,
        limit: int = 50
    ) -> List[Question]:
        """Get questions by category."""
        return await self.find_many(
            query={"category": category.value, "is_active": True},
            sort=[("points", ASCENDING)],
            limit=limit
        )
    
    async def search_questions(
        self,
        query: str,
        limit: int = 20
    ) -> List[Question]:
        """Search questions by text (English or Hindi)."""
        search_query = {
            "is_active": True,
            "$or": [
                {"question_text_en": {"$regex": query, "$options": "i"}},
                {"question_text_hi": {"$regex": query, "$options": "i"}}
            ]
        }
        return await self.find_many(query=search_query, limit=limit)
    
    async def deactivate(self, question_id: str) -> bool:
        """Soft delete a question."""
        return await self.update_by_id(
            question_id,
            {"$set": {"is_active": False}}
        )


class TemplateRepository(BaseRepository[Template]):
    """Repository for Question Template operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "templates", Template)
    
    async def get_active_templates(
        self,
        match_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Template]:
        """Get active templates with optional match type filter."""
        query = {"is_active": True}
        if match_type:
            query["match_type"] = match_type
        
        return await self.find_many(
            query=query,
            sort=[("name", ASCENDING)],
            limit=limit
        )
    
    async def get_with_questions(
        self,
        template_id: str,
        question_repo: QuestionRepository
    ) -> Optional[dict]:
        """Get template with its full questions."""
        template = await self.find_by_id(template_id)
        if not template:
            return None
        
        questions = await question_repo.get_by_ids(template.question_ids)
        
        # Sort questions to match template order
        question_map = {q.id: q for q in questions}
        ordered_questions = [
            question_map.get(qid) 
            for qid in template.question_ids 
            if qid in question_map
        ]
        
        return {
            "template": template,
            "questions": ordered_questions
        }
    
    async def validate_questions(
        self,
        question_ids: List[str],
        question_repo: QuestionRepository
    ) -> tuple[bool, str]:
        """
        Validate that all questions exist and are active.
        Returns (is_valid, error_message).
        """
        if len(question_ids) != 11:
            return False, "Template must have exactly 11 questions"
        
        # Check for duplicates
        if len(set(question_ids)) != 11:
            return False, "Template contains duplicate questions"
        
        # Verify all questions exist and are active
        questions = await question_repo.get_by_ids(question_ids)
        
        if len(questions) != 11:
            return False, f"Only {len(questions)} of 11 questions found"
        
        inactive = [q.id for q in questions if not q.is_active]
        if inactive:
            return False, f"Questions {inactive} are inactive"
        
        return True, ""
    
    async def calculate_total_points(
        self,
        question_ids: List[str],
        question_repo: QuestionRepository
    ) -> int:
        """Calculate total points for a template's questions."""
        questions = await question_repo.get_by_ids(question_ids)
        return sum(q.points * q.multiplier for q in questions)
    
    async def deactivate(self, template_id: str) -> bool:
        """Soft delete a template."""
        return await self.update_by_id(
            template_id,
            {"$set": {"is_active": False}}
        )
