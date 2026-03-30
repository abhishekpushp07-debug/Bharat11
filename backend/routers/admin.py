"""
Admin Router - Questions & Templates Management
Handles CRUD for questions bank and match templates.
Admin-only endpoints (future: admin role check).
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import get_db
from core.dependencies import CurrentUser, AdminUser
from core.exceptions import CrickPredictException
from models.schemas import (
    Question, QuestionOption, EvaluationRules,
    QuestionCategory, QuestionDifficulty, EvaluationType,
    User, generate_id, utc_now
)


router = APIRouter(prefix="/admin", tags=["Admin"])


# ==================== DTOs ====================

class QuestionOptionCreate(BaseModel):
    key: str = Field(..., pattern="^[A-D]$")
    text_en: str
    text_hi: str = ""


class EvaluationRulesCreate(BaseModel):
    type: EvaluationType = EvaluationType.EXACT_MATCH
    source_field: str = ""
    condition: str = ""
    threshold: float = 0
    bonus_multiplier: float = 1.0


class QuestionCreate(BaseModel):
    question_text_en: str
    question_text_hi: str = ""
    category: QuestionCategory = QuestionCategory.MATCH_OUTCOME
    difficulty: QuestionDifficulty = QuestionDifficulty.EASY
    options: list[QuestionOptionCreate] = Field(..., min_length=2, max_length=4)
    points: int = Field(default=10, ge=1, le=100)
    evaluation_rules: Optional[EvaluationRulesCreate] = None
    is_active: bool = True


class QuestionUpdate(BaseModel):
    question_text_en: Optional[str] = None
    question_text_hi: Optional[str] = None
    category: Optional[QuestionCategory] = None
    difficulty: Optional[QuestionDifficulty] = None
    options: Optional[list[QuestionOptionCreate]] = None
    points: Optional[int] = None
    evaluation_rules: Optional[EvaluationRulesCreate] = None
    is_active: Optional[bool] = None


class TemplateCreate(BaseModel):
    name: str
    description: str = ""
    match_type: str = "T20"
    question_ids: list[str] = Field(..., min_length=1, max_length=15)
    is_active: bool = True


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    match_type: Optional[str] = None
    question_ids: Optional[list[str]] = None
    is_active: Optional[bool] = None


class BulkQuestionImport(BaseModel):
    questions: list[QuestionCreate]


# ==================== QUESTION ENDPOINTS ====================

@router.get(
    "/questions",
    summary="List all questions",
    description="Get paginated list of questions with optional category filter"
)
async def list_questions(
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db),
    category: Optional[QuestionCategory] = None,
    difficulty: Optional[QuestionDifficulty] = None,
    is_active: Optional[bool] = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100)
):
    query = {}
    if category:
        query["category"] = category.value
    if difficulty:
        query["difficulty"] = difficulty.value
    if is_active is not None:
        query["is_active"] = is_active

    skip = (page - 1) * limit
    cursor = db.questions.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
    questions = await cursor.to_list(length=limit)
    total = await db.questions.count_documents(query)

    return {
        "questions": questions,
        "page": page,
        "limit": limit,
        "total": total,
        "has_more": (page * limit) < total
    }


@router.get(
    "/questions/{question_id}",
    summary="Get question by ID"
)
async def get_question(
    question_id: str,
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    question = await db.questions.find_one({"id": question_id}, {"_id": 0})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.post(
    "/questions",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new question"
)
async def create_question(
    data: QuestionCreate,
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    now = utc_now().isoformat()
    question = {
        "id": generate_id(),
        "question_text_en": data.question_text_en,
        "question_text_hi": data.question_text_hi,
        "category": data.category.value,
        "difficulty": data.difficulty.value,
        "options": [o.model_dump() for o in data.options],
        "points": data.points,
        "evaluation_rules": data.evaluation_rules.model_dump() if data.evaluation_rules else {
            "type": "exact_match", "source_field": "", "condition": "",
            "threshold": 0, "bonus_multiplier": 1.0
        },
        "correct_option": None,
        "is_active": data.is_active,
        "created_at": now,
        "updated_at": now
    }
    await db.questions.insert_one(question)
    del question["_id"]
    return question


@router.put(
    "/questions/{question_id}",
    summary="Update a question"
)
async def update_question(
    question_id: str,
    data: QuestionUpdate,
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    existing = await db.questions.find_one({"id": question_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Question not found")

    update_fields = {}
    update_data = data.model_dump(exclude_none=True)
    for key, value in update_data.items():
        if key == "options":
            update_fields["options"] = [o.model_dump() if hasattr(o, 'model_dump') else o for o in value]
        elif key == "evaluation_rules":
            update_fields["evaluation_rules"] = value.model_dump() if hasattr(value, 'model_dump') else value
        elif key == "category":
            update_fields["category"] = value.value if hasattr(value, 'value') else value
        elif key == "difficulty":
            update_fields["difficulty"] = value.value if hasattr(value, 'value') else value
        else:
            update_fields[key] = value

    if update_fields:
        update_fields["updated_at"] = utc_now().isoformat()
        await db.questions.update_one({"id": question_id}, {"$set": update_fields})

    updated = await db.questions.find_one({"id": question_id}, {"_id": 0})
    return updated


@router.delete(
    "/questions/{question_id}",
    summary="Delete a question"
)
async def delete_question(
    question_id: str,
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    result = await db.questions.delete_one({"id": question_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted", "id": question_id}


@router.post(
    "/questions/bulk-import",
    status_code=status.HTTP_201_CREATED,
    summary="Bulk import questions from JSON"
)
async def bulk_import_questions(
    data: BulkQuestionImport,
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    now = utc_now().isoformat()
    docs = []
    for q in data.questions:
        doc = {
            "id": generate_id(),
            "question_text_en": q.question_text_en,
            "question_text_hi": q.question_text_hi,
            "category": q.category.value,
            "difficulty": q.difficulty.value,
            "options": [o.model_dump() for o in q.options],
            "points": q.points,
            "evaluation_rules": q.evaluation_rules.model_dump() if q.evaluation_rules else {
                "type": "exact_match", "source_field": "", "condition": "",
                "threshold": 0, "bonus_multiplier": 1.0
            },
            "correct_option": None,
            "is_active": q.is_active,
            "created_at": now,
            "updated_at": now
        }
        docs.append(doc)

    if docs:
        await db.questions.insert_many(docs)

    return {"imported": len(docs), "message": f"{len(docs)} questions imported successfully"}


# ==================== TEMPLATE ENDPOINTS ====================

@router.get(
    "/templates",
    summary="List all templates"
)
async def list_templates(
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db),
    match_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=50)
):
    query = {}
    if match_type:
        query["match_type"] = match_type
    if is_active is not None:
        query["is_active"] = is_active

    skip = (page - 1) * limit
    cursor = db.templates.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
    templates = await cursor.to_list(length=limit)
    total = await db.templates.count_documents(query)

    return {
        "templates": templates,
        "page": page,
        "limit": limit,
        "total": total,
        "has_more": (page * limit) < total
    }


@router.get(
    "/templates/{template_id}",
    summary="Get template with resolved questions"
)
async def get_template(
    template_id: str,
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    template = await db.templates.find_one({"id": template_id}, {"_id": 0})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Resolve questions
    question_ids = template.get("question_ids", [])
    if question_ids:
        cursor = db.questions.find({"id": {"$in": question_ids}}, {"_id": 0})
        questions = await cursor.to_list(length=len(question_ids))
        # Maintain order
        q_map = {q["id"]: q for q in questions}
        template["questions"] = [q_map[qid] for qid in question_ids if qid in q_map]
    else:
        template["questions"] = []

    return template


@router.post(
    "/templates",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new template"
)
async def create_template(
    data: TemplateCreate,
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    # Validate question IDs exist
    existing_count = await db.questions.count_documents({"id": {"$in": data.question_ids}})
    if existing_count != len(data.question_ids):
        raise HTTPException(status_code=400, detail=f"Some question IDs are invalid. Found {existing_count} of {len(data.question_ids)}")

    # Calculate total points
    cursor = db.questions.find({"id": {"$in": data.question_ids}}, {"_id": 0, "points": 1})
    questions = await cursor.to_list(length=len(data.question_ids))
    total_points = sum(q.get("points", 10) for q in questions)

    now = utc_now().isoformat()
    template = {
        "id": generate_id(),
        "name": data.name,
        "description": data.description,
        "match_type": data.match_type,
        "question_ids": data.question_ids,
        "total_points": total_points,
        "question_count": len(data.question_ids),
        "is_active": data.is_active,
        "created_at": now,
        "updated_at": now
    }
    await db.templates.insert_one(template)
    del template["_id"]
    return template


@router.put(
    "/templates/{template_id}",
    summary="Update a template"
)
async def update_template(
    template_id: str,
    data: TemplateUpdate,
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    existing = await db.templates.find_one({"id": template_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Template not found")

    update_fields = data.model_dump(exclude_none=True)

    if "question_ids" in update_fields:
        qids = update_fields["question_ids"]
        existing_count = await db.questions.count_documents({"id": {"$in": qids}})
        if existing_count != len(qids):
            raise HTTPException(status_code=400, detail="Some question IDs are invalid")

        cursor = db.questions.find({"id": {"$in": qids}}, {"_id": 0, "points": 1})
        questions = await cursor.to_list(length=len(qids))
        update_fields["total_points"] = sum(q.get("points", 10) for q in questions)
        update_fields["question_count"] = len(qids)

    if update_fields:
        update_fields["updated_at"] = utc_now().isoformat()
        await db.templates.update_one({"id": template_id}, {"$set": update_fields})

    updated = await db.templates.find_one({"id": template_id}, {"_id": 0})
    return updated


@router.delete(
    "/templates/{template_id}",
    summary="Delete a template"
)
async def delete_template(
    template_id: str,
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    result = await db.templates.delete_one({"id": template_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted", "id": template_id}


@router.post(
    "/templates/{template_id}/clone",
    status_code=status.HTTP_201_CREATED,
    summary="Clone an existing template"
)
async def clone_template(
    template_id: str,
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    original = await db.templates.find_one({"id": template_id}, {"_id": 0})
    if not original:
        raise HTTPException(status_code=404, detail="Template not found")

    now = utc_now().isoformat()
    clone = {
        **original,
        "id": generate_id(),
        "name": f"{original['name']} (Copy)",
        "created_at": now,
        "updated_at": now
    }
    await db.templates.insert_one(clone)
    del clone["_id"]
    return clone
