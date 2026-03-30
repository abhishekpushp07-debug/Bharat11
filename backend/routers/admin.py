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
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class AutoResolutionConfig(BaseModel):
    """Config for auto-settlement using live scorecard data."""
    metric: str = ""  # e.g., "innings_1_total_runs", "match_total_sixes", "match_winner"
    trigger: str = "match_end"  # "innings_1_end", "innings_2_end", "match_end", "toss"
    resolution_type: str = "range"  # "range", "text_match", "boolean"
    threshold: Optional[float] = None  # For boolean type
    comparator: Optional[str] = None  # ">=", ">", "<=", "<", "=="


class EvaluationRulesCreate(BaseModel):
    type: EvaluationType = EvaluationType.EXACT_MATCH
    source_field: str = ""
    condition: str = ""
    threshold: float = 0
    bonus_multiplier: float = 1.0


class QuestionCreate(BaseModel):
    question_text_en: str
    question_text_hi: str = ""
    category: QuestionCategory = QuestionCategory.MATCH
    difficulty: QuestionDifficulty = QuestionDifficulty.EASY
    options: list[QuestionOptionCreate] = Field(..., min_length=2, max_length=4)
    points: int = Field(default=10, ge=1, le=200)
    evaluation_rules: Optional[EvaluationRulesCreate] = None
    auto_resolution: Optional[AutoResolutionConfig] = None
    is_active: bool = True


class QuestionUpdate(BaseModel):
    question_text_en: Optional[str] = None
    question_text_hi: Optional[str] = None
    category: Optional[QuestionCategory] = None
    difficulty: Optional[QuestionDifficulty] = None
    options: Optional[list[QuestionOptionCreate]] = None
    points: Optional[int] = None
    evaluation_rules: Optional[EvaluationRulesCreate] = None
    auto_resolution: Optional[AutoResolutionConfig] = None
    is_active: Optional[bool] = None


class TemplateCreate(BaseModel):
    name: str
    description: str = ""
    match_type: str = "T20"
    template_type: str = "full_match"
    question_ids: list[str] = Field(..., min_length=1, max_length=20)
    is_active: bool = True
    is_default: bool = False


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    match_type: Optional[str] = None
    template_type: Optional[str] = None
    question_ids: Optional[list[str]] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


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
        "auto_resolution": data.auto_resolution.model_dump() if data.auto_resolution else None,
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
        elif key == "auto_resolution":
            update_fields["auto_resolution"] = value.model_dump() if hasattr(value, 'model_dump') else value
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
            "auto_resolution": q.auto_resolution.model_dump() if q.auto_resolution else None,
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

    # If setting as default, unset other defaults of same type
    if data.is_default:
        await db.templates.update_many(
            {"template_type": data.template_type, "is_default": True},
            {"$set": {"is_default": False}}
        )

    template = {
        "id": generate_id(),
        "name": data.name,
        "description": data.description,
        "match_type": data.match_type,
        "template_type": data.template_type,
        "question_ids": data.question_ids,
        "total_points": total_points,
        "question_count": len(data.question_ids),
        "is_active": data.is_active,
        "is_default": data.is_default,
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
        "is_default": False,
        "created_at": now,
        "updated_at": now
    }
    await db.templates.insert_one(clone)
    del clone["_id"]
    return clone


@router.post(
    "/templates/{template_id}/set-default",
    summary="Set a template as the default for its type"
)
async def set_template_default(
    template_id: str,
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    template = await db.templates.find_one({"id": template_id}, {"_id": 0})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    t_type = template.get("template_type", "full_match")
    # Unset other defaults of same type
    await db.templates.update_many(
        {"template_type": t_type, "is_default": True},
        {"$set": {"is_default": False}}
    )
    await db.templates.update_one(
        {"id": template_id},
        {"$set": {"is_default": True, "updated_at": utc_now().isoformat()}}
    )
    return {"message": f"Template '{template['name']}' set as default {t_type}", "id": template_id}


# ==================== CONTEST CREATION ====================

class ContestCreate(BaseModel):
    match_id: str
    template_id: str
    name: str
    entry_fee: int = Field(default=1000, ge=0)
    prize_pool: int = Field(default=0, ge=0)
    max_participants: int = Field(default=1000, ge=2)
    prize_distribution: list[dict] = Field(default_factory=list)


@router.post(
    "/contests",
    status_code=status.HTTP_201_CREATED,
    summary="Create a contest for a match"
)
async def admin_create_contest(
    data: ContestCreate,
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    # Validate match exists
    match = await db.matches.find_one({"id": data.match_id}, {"_id": 0})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Validate template exists
    template = await db.templates.find_one({"id": data.template_id}, {"_id": 0})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    from datetime import timedelta
    start_time = match.get("start_time", "")
    if isinstance(start_time, str):
        from datetime import datetime as dt
        try:
            start_time = dt.fromisoformat(start_time.replace('Z', '+00:00'))
        except Exception:
            start_time = utc_now() + timedelta(hours=1)

    now = utc_now().isoformat()
    contest = {
        "id": generate_id(),
        "match_id": data.match_id,
        "template_id": data.template_id,
        "name": data.name,
        "entry_fee": data.entry_fee,
        "prize_pool": data.prize_pool,
        "max_participants": data.max_participants,
        "current_participants": 0,
        "prize_distribution": data.prize_distribution or [
            {"rank_start": 1, "rank_end": 1, "prize": int(data.prize_pool * 0.5)},
            {"rank_start": 2, "rank_end": 3, "prize": int(data.prize_pool * 0.15)},
            {"rank_start": 4, "rank_end": 10, "prize": int(data.prize_pool * 0.05)},
        ],
        "status": "open",
        "lock_time": (start_time - timedelta(minutes=15)).isoformat() if hasattr(start_time, 'isoformat') else start_time,
        "created_at": now,
        "updated_at": now
    }
    await db.contests.insert_one(contest)
    del contest["_id"]

    # Auto-assign template to match if not already
    templates_assigned = match.get("templates_assigned", [])
    if data.template_id not in templates_assigned:
        templates_assigned.append(data.template_id)
        await db.matches.update_one(
            {"id": data.match_id},
            {"$set": {"templates_assigned": templates_assigned}}
        )

    return contest


# ==================== MATCH TEMPLATE MANAGEMENT ====================

@router.post(
    "/matches/{match_id}/assign-templates",
    summary="Assign templates to match (1 full_match required, max 5 total)"
)
async def assign_templates_to_match(
    match_id: str,
    template_ids: list[str],
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    match = await db.matches.find_one({"id": match_id}, {"_id": 0})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if len(template_ids) > 5:
        raise HTTPException(status_code=400, detail="Max 5 templates per match")

    # Fetch templates and validate
    cursor = db.templates.find({"id": {"$in": template_ids}}, {"_id": 0})
    templates = await cursor.to_list(length=len(template_ids))

    if len(templates) != len(template_ids):
        raise HTTPException(status_code=400, detail="Some template IDs are invalid")

    full_match_count = sum(1 for t in templates if t.get("template_type", "full_match") == "full_match")
    in_match_count = sum(1 for t in templates if t.get("template_type") == "in_match")

    if full_match_count < 1:
        raise HTTPException(status_code=400, detail="At least 1 full_match template is required")
    if in_match_count > 4:
        raise HTTPException(status_code=400, detail="Max 4 in_match templates allowed")

    await db.matches.update_one(
        {"id": match_id},
        {"$set": {"templates_assigned": template_ids, "updated_at": utc_now().isoformat()}}
    )

    return {
        "match_id": match_id,
        "templates_assigned": template_ids,
        "full_match": full_match_count,
        "in_match": in_match_count
    }


@router.get(
    "/matches/{match_id}/templates",
    summary="Get templates assigned to a match"
)
async def get_match_templates(
    match_id: str,
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    match = await db.matches.find_one({"id": match_id}, {"_id": 0})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    template_ids = match.get("templates_assigned", [])
    if not template_ids:
        # Return default templates
        default_full = await db.templates.find_one(
            {"template_type": "full_match", "is_default": True, "is_active": True},
            {"_id": 0}
        )
        if default_full:
            return {"templates": [default_full], "using_defaults": True}
        return {"templates": [], "using_defaults": True}

    cursor = db.templates.find({"id": {"$in": template_ids}}, {"_id": 0})
    templates = await cursor.to_list(length=len(template_ids))
    return {"templates": templates, "using_defaults": False}


# ==================== ADMIN STATS ====================

@router.get(
    "/stats",
    summary="Get admin dashboard stats"
)
async def get_admin_stats(
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    total_users = await db.users.count_documents({})
    total_matches = await db.matches.count_documents({})
    total_contests = await db.contests.count_documents({})
    total_questions = await db.questions.count_documents({})
    total_templates = await db.templates.count_documents({})
    live_matches = await db.matches.count_documents({"status": "live"})
    upcoming_matches = await db.matches.count_documents({"status": "upcoming"})
    open_contests = await db.contests.count_documents({"status": "open"})
    active_entries = await db.contest_entries.count_documents({})

    return {
        "users": total_users,
        "matches": total_matches,
        "contests": total_contests,
        "questions": total_questions,
        "templates": total_templates,
        "live_matches": live_matches,
        "upcoming_matches": upcoming_matches,
        "open_contests": open_contests,
        "active_entries": active_entries
    }



# ==================== AUTO-SETTLEMENT ENGINE ====================

@router.post(
    "/settlement/{match_id}/run",
    summary="Run auto-settlement for a match",
    description="Fetch scorecard, evaluate questions, auto-resolve & auto-finalize"
)
async def run_auto_settlement(
    match_id: str,
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    from services.settlement_engine import run_settlement_for_match
    result = await run_settlement_for_match(match_id, db)
    return result


@router.get(
    "/settlement/{match_id}/metrics",
    summary="Get parsed scorecard metrics for a match",
    description="Fetches scorecard from CricketData.org and returns parsed metrics"
)
async def get_match_metrics(
    match_id: str,
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    from services.settlement_engine import fetch_match_metrics
    return await fetch_match_metrics(match_id, db)


@router.get(
    "/settlement/{match_id}/scorecard",
    summary="Get raw scorecard data from CricketData.org",
    description="Returns full scorecard with batting/bowling/catching details"
)
async def get_match_scorecard(
    match_id: str,
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    from services.cricket_data import cricket_service

    match = await db.matches.find_one({"id": match_id}, {"_id": 0})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Try cricketdata_id first, then external_match_id
    cd_id = match.get("cricketdata_id") or match.get("external_match_id", "")
    if not cd_id:
        raise HTTPException(status_code=400, detail="No CricketData ID linked. Sync or link match first.")

    data = await cricket_service.get_scorecard(cd_id)
    if not data:
        raise HTTPException(status_code=502, detail="Could not fetch scorecard from API")

    return {
        "match_id": match_id,
        "cricketdata_id": cd_id,
        "scorecard": data
    }


class LinkCricketDataID(BaseModel):
    cricketdata_id: str


@router.post(
    "/settlement/{match_id}/link",
    summary="Manually link a CricketData.org match ID"
)
async def link_cricketdata_id(
    match_id: str,
    data: LinkCricketDataID,
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    match = await db.matches.find_one({"id": match_id})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    await db.matches.update_one(
        {"id": match_id},
        {"$set": {"cricketdata_id": data.cricketdata_id, "updated_at": utc_now().isoformat()}}
    )
    return {"match_id": match_id, "cricketdata_id": data.cricketdata_id, "linked": True}


@router.get(
    "/settlement/status",
    summary="Get settlement status for all active matches"
)
async def get_settlement_status(
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    # Get matches with active contests
    active_matches = await db.matches.find(
        {"status": {"$in": ["live", "completed"]}},
        {"_id": 0, "id": 1, "team_a": 1, "team_b": 1, "status": 1, "external_match_id": 1}
    ).sort("updated_at", -1).to_list(length=20)

    result = []
    for match in active_matches:
        mid = match["id"]
        # Count contests and resolved questions
        contests = await db.contests.find(
            {"match_id": mid},
            {"_id": 0, "id": 1, "status": 1, "template_id": 1}
        ).to_list(length=10)

        total_q = 0
        resolved_q = 0
        for c in contests:
            tmpl = await db.templates.find_one({"id": c.get("template_id")}, {"_id": 0, "question_ids": 1})
            if tmpl:
                qids = tmpl.get("question_ids", [])
                total_q += len(qids)
                rcount = await db.question_results.count_documents({
                    "match_id": mid, "question_id": {"$in": qids}
                })
                resolved_q += rcount

        result.append({
            "match_id": mid,
            "team_a": match.get("team_a", {}),
            "team_b": match.get("team_b", {}),
            "match_status": match.get("status"),
            "has_external_id": bool(match.get("external_match_id")),
            "contests_count": len(contests),
            "total_questions": total_q,
            "resolved_questions": resolved_q,
            "settlement_progress": f"{resolved_q}/{total_q}" if total_q > 0 else "N/A"
        })

    return {"matches": result}


@router.post(
    "/questions/bulk-import-with-auto",
    status_code=201,
    summary="Bulk import questions with auto-resolution rules (for auto-settlement)"
)
async def bulk_import_auto_questions(
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Seed a standard set of auto-resolvable questions for IPL T20 matches.
    These questions have auto_resolution rules that the settlement engine evaluates.
    """
    now = utc_now().isoformat()
    questions = [
        {
            "question_text_en": "What will be the 1st innings total score?",
            "question_text_hi": "Pehli innings ka total score kitna hoga?",
            "category": "match",
            "difficulty": "medium",
            "points": 50,
            "auto_resolution": {"metric": "innings_1_total_runs", "trigger": "innings_1_end", "resolution_type": "range"},
            "options": [
                {"key": "A", "text_en": "0-140 runs", "text_hi": "0-140 runs", "min_value": 0, "max_value": 140},
                {"key": "B", "text_en": "141-170 runs", "text_hi": "141-170 runs", "min_value": 141, "max_value": 170},
                {"key": "C", "text_en": "171-200 runs", "text_hi": "171-200 runs", "min_value": 171, "max_value": 200},
                {"key": "D", "text_en": "200+ runs", "text_hi": "200+ runs", "min_value": 201, "max_value": 999},
            ]
        },
        {
            "question_text_en": "What will be the 2nd innings total score?",
            "question_text_hi": "Doosri innings ka total score kitna hoga?",
            "category": "match",
            "difficulty": "medium",
            "points": 50,
            "auto_resolution": {"metric": "innings_2_total_runs", "trigger": "match_end", "resolution_type": "range"},
            "options": [
                {"key": "A", "text_en": "0-140 runs", "text_hi": "0-140 runs", "min_value": 0, "max_value": 140},
                {"key": "B", "text_en": "141-170 runs", "text_hi": "141-170 runs", "min_value": 141, "max_value": 170},
                {"key": "C", "text_en": "171-200 runs", "text_hi": "171-200 runs", "min_value": 171, "max_value": 200},
                {"key": "D", "text_en": "200+ runs", "text_hi": "200+ runs", "min_value": 201, "max_value": 999},
            ]
        },
        {
            "question_text_en": "Total sixes in the match?",
            "question_text_hi": "Match mein total kitne sixes lagenge?",
            "category": "batting",
            "difficulty": "medium",
            "points": 40,
            "auto_resolution": {"metric": "match_total_sixes", "trigger": "match_end", "resolution_type": "range"},
            "options": [
                {"key": "A", "text_en": "0-8 sixes", "text_hi": "0-8 sixes", "min_value": 0, "max_value": 8},
                {"key": "B", "text_en": "9-14 sixes", "text_hi": "9-14 sixes", "min_value": 9, "max_value": 14},
                {"key": "C", "text_en": "15-20 sixes", "text_hi": "15-20 sixes", "min_value": 15, "max_value": 20},
                {"key": "D", "text_en": "21+ sixes", "text_hi": "21+ sixes", "min_value": 21, "max_value": 999},
            ]
        },
        {
            "question_text_en": "Total fours in the match?",
            "question_text_hi": "Match mein total kitne fours lagenge?",
            "category": "batting",
            "difficulty": "medium",
            "points": 40,
            "auto_resolution": {"metric": "match_total_fours", "trigger": "match_end", "resolution_type": "range"},
            "options": [
                {"key": "A", "text_en": "0-16 fours", "text_hi": "0-16 fours", "min_value": 0, "max_value": 16},
                {"key": "B", "text_en": "17-24 fours", "text_hi": "17-24 fours", "min_value": 17, "max_value": 24},
                {"key": "C", "text_en": "25-32 fours", "text_hi": "25-32 fours", "min_value": 25, "max_value": 32},
                {"key": "D", "text_en": "33+ fours", "text_hi": "33+ fours", "min_value": 33, "max_value": 999},
            ]
        },
        {
            "question_text_en": "1st innings wickets fallen?",
            "question_text_hi": "Pehli innings mein kitne wicket girenge?",
            "category": "bowling",
            "difficulty": "easy",
            "points": 30,
            "auto_resolution": {"metric": "innings_1_total_wickets", "trigger": "innings_1_end", "resolution_type": "range"},
            "options": [
                {"key": "A", "text_en": "0-4 wickets", "text_hi": "0-4 wickets", "min_value": 0, "max_value": 4},
                {"key": "B", "text_en": "5-6 wickets", "text_hi": "5-6 wickets", "min_value": 5, "max_value": 6},
                {"key": "C", "text_en": "7-8 wickets", "text_hi": "7-8 wickets", "min_value": 7, "max_value": 8},
                {"key": "D", "text_en": "9-10 wickets", "text_hi": "9-10 wickets", "min_value": 9, "max_value": 10},
            ]
        },
        {
            "question_text_en": "Total match runs (both innings combined)?",
            "question_text_hi": "Dono innings ka total milake kitne runs honge?",
            "category": "match",
            "difficulty": "hard",
            "points": 60,
            "auto_resolution": {"metric": "match_total_runs", "trigger": "match_end", "resolution_type": "range"},
            "options": [
                {"key": "A", "text_en": "0-300 runs", "text_hi": "0-300 runs", "min_value": 0, "max_value": 300},
                {"key": "B", "text_en": "301-340 runs", "text_hi": "301-340 runs", "min_value": 301, "max_value": 340},
                {"key": "C", "text_en": "341-380 runs", "text_hi": "341-380 runs", "min_value": 341, "max_value": 380},
                {"key": "D", "text_en": "381+ runs", "text_hi": "381+ runs", "min_value": 381, "max_value": 999},
            ]
        },
        {
            "question_text_en": "1st innings total sixes?",
            "question_text_hi": "Pehli innings mein kitne sixes?",
            "category": "batting",
            "difficulty": "easy",
            "points": 30,
            "auto_resolution": {"metric": "innings_1_total_sixes", "trigger": "innings_1_end", "resolution_type": "range"},
            "options": [
                {"key": "A", "text_en": "0-4 sixes", "text_hi": "0-4 sixes", "min_value": 0, "max_value": 4},
                {"key": "B", "text_en": "5-8 sixes", "text_hi": "5-8 sixes", "min_value": 5, "max_value": 8},
                {"key": "C", "text_en": "9-12 sixes", "text_hi": "9-12 sixes", "min_value": 9, "max_value": 12},
                {"key": "D", "text_en": "13+ sixes", "text_hi": "13+ sixes", "min_value": 13, "max_value": 999},
            ]
        },
        {
            "question_text_en": "Total extras in the match?",
            "question_text_hi": "Match mein total kitne extras honge?",
            "category": "special",
            "difficulty": "hard",
            "points": 40,
            "auto_resolution": {"metric": "match_total_extras", "trigger": "match_end", "resolution_type": "range"},
            "options": [
                {"key": "A", "text_en": "0-10 extras", "text_hi": "0-10 extras", "min_value": 0, "max_value": 10},
                {"key": "B", "text_en": "11-18 extras", "text_hi": "11-18 extras", "min_value": 11, "max_value": 18},
                {"key": "C", "text_en": "19-25 extras", "text_hi": "19-25 extras", "min_value": 19, "max_value": 25},
                {"key": "D", "text_en": "26+ extras", "text_hi": "26+ extras", "min_value": 26, "max_value": 999},
            ]
        },
        {
            "question_text_en": "Highest individual score in the match?",
            "question_text_hi": "Match mein sabse zyada individual score kitna hoga?",
            "category": "player_performance",
            "difficulty": "hard",
            "points": 50,
            "auto_resolution": {"metric": "highest_run_scorer_runs", "trigger": "match_end", "resolution_type": "range"},
            "options": [
                {"key": "A", "text_en": "0-35 runs", "text_hi": "0-35 runs", "min_value": 0, "max_value": 35},
                {"key": "B", "text_en": "36-60 runs", "text_hi": "36-60 runs", "min_value": 36, "max_value": 60},
                {"key": "C", "text_en": "61-85 runs", "text_hi": "61-85 runs", "min_value": 61, "max_value": 85},
                {"key": "D", "text_en": "86+ runs", "text_hi": "86+ runs", "min_value": 86, "max_value": 999},
            ]
        },
        {
            "question_text_en": "Best bowler wickets in match?",
            "question_text_hi": "Match ke best bowler ke kitne wickets honge?",
            "category": "bowling",
            "difficulty": "medium",
            "points": 40,
            "auto_resolution": {"metric": "best_bowler_wickets", "trigger": "match_end", "resolution_type": "range"},
            "options": [
                {"key": "A", "text_en": "0-1 wickets", "text_hi": "0-1 wickets", "min_value": 0, "max_value": 1},
                {"key": "B", "text_en": "2-3 wickets", "text_hi": "2-3 wickets", "min_value": 2, "max_value": 3},
                {"key": "C", "text_en": "4-5 wickets", "text_hi": "4-5 wickets", "min_value": 4, "max_value": 5},
                {"key": "D", "text_en": "6+ wickets", "text_hi": "6+ wickets", "min_value": 6, "max_value": 10},
            ]
        },
        {
            "question_text_en": "1st innings run rate?",
            "question_text_hi": "Pehli innings ka run rate kitna hoga?",
            "category": "match",
            "difficulty": "medium",
            "points": 35,
            "auto_resolution": {"metric": "innings_1_run_rate", "trigger": "innings_1_end", "resolution_type": "range"},
            "options": [
                {"key": "A", "text_en": "Below 7.0", "text_hi": "7.0 se kam", "min_value": 0, "max_value": 6.99},
                {"key": "B", "text_en": "7.0 - 8.5", "text_hi": "7.0 - 8.5", "min_value": 7.0, "max_value": 8.5},
                {"key": "C", "text_en": "8.6 - 10.0", "text_hi": "8.6 - 10.0", "min_value": 8.6, "max_value": 10.0},
                {"key": "D", "text_en": "Above 10.0", "text_hi": "10.0 se zyada", "min_value": 10.01, "max_value": 99},
            ]
        },
    ]

    docs = []
    for q in questions:
        doc = {
            "id": generate_id(),
            "question_text_en": q["question_text_en"],
            "question_text_hi": q["question_text_hi"],
            "category": q["category"],
            "difficulty": q["difficulty"],
            "options": q["options"],
            "points": q["points"],
            "evaluation_rules": {"type": "exact_match", "source_field": "", "condition": "", "threshold": 0, "bonus_multiplier": 1.0},
            "auto_resolution": q["auto_resolution"],
            "correct_option": None,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
        docs.append(doc)

    if docs:
        await db.questions.insert_many(docs)

    # Auto-create default template with these questions
    q_ids = [d["id"] for d in docs]
    total_pts = sum(d["points"] for d in docs)
    template = {
        "id": generate_id(),
        "name": "Auto-Settlement T20 Template",
        "description": "11 questions with auto-resolution rules for T20 matches",
        "match_type": "T20",
        "template_type": "full_match",
        "question_ids": q_ids,
        "total_points": total_pts,
        "question_count": len(q_ids),
        "is_active": True,
        "is_default": True,
        "created_at": now,
        "updated_at": now
    }
    # Unset previous defaults
    await db.templates.update_many(
        {"template_type": "full_match", "is_default": True},
        {"$set": {"is_default": False}}
    )
    await db.templates.insert_one(template)

    return {
        "imported": len(docs),
        "template_id": template["id"],
        "template_name": template["name"],
        "total_points": total_pts,
        "message": f"{len(docs)} auto-resolvable questions + 1 default template created!"
    }
