"""
Match Router
Handles match listing, details, and live score endpoints for users.
Admin endpoints for match creation and management.
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Annotated, Optional
from pydantic import BaseModel, Field

from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import get_db
from core.dependencies import CurrentUser
from models.schemas import MatchStatus, generate_id, utc_now


router = APIRouter(prefix="/matches", tags=["Matches"])


# ==================== DTOs ====================

class TeamCreate(BaseModel):
    name: str
    short_name: str
    logo_url: str = ""


class MatchCreate(BaseModel):
    team_a: TeamCreate
    team_b: TeamCreate
    match_type: str = "T20"
    venue: str = ""
    start_time: str  # ISO format
    tournament: str = "IPL 2026"
    template_id: Optional[str] = None


class MatchStatusUpdate(BaseModel):
    status: MatchStatus


class LiveScoreUpdate(BaseModel):
    batting_team: str
    score: str
    overs: str
    wickets: int = 0
    run_rate: float = 0.0
    required_rate: Optional[float] = None
    last_ball: str = ""
    partnership: str = ""
    batsmen: list = Field(default_factory=list)
    bowler: dict = Field(default_factory=dict)


# ==================== USER ENDPOINTS ====================

@router.get(
    "",
    summary="List matches",
    description="Get matches filtered by status (upcoming, live, completed)"
)
async def list_matches(
    db: AsyncIOMotorDatabase = Depends(get_db),
    match_status: Optional[str] = Query(default=None, alias="status"),
    limit: int = Query(default=20, ge=1, le=50),
    page: int = Query(default=1, ge=1)
):
    query = {}
    if match_status:
        query["status"] = match_status

    skip = (page - 1) * limit
    cursor = db.matches.find(query, {"_id": 0}).sort("start_time", 1).skip(skip).limit(limit)
    matches = await cursor.to_list(length=limit)
    total = await db.matches.count_documents(query)

    return {
        "matches": matches,
        "page": page,
        "limit": limit,
        "total": total,
        "has_more": (page * limit) < total
    }


@router.get(
    "/{match_id}",
    summary="Get match details",
    description="Get match details including teams, venue, scores, and linked contests"
)
async def get_match(
    match_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    match = await db.matches.find_one({"id": match_id}, {"_id": 0})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Count linked contests
    contest_count = await db.contests.count_documents({"match_id": match_id})
    match["contests_count"] = contest_count

    return match


@router.get(
    "/{match_id}/live-score",
    summary="Get live score",
    description="Get current live score for a match"
)
async def get_live_score(
    match_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    match = await db.matches.find_one({"id": match_id}, {"_id": 0, "id": 1, "status": 1, "live_score": 1, "team_a": 1, "team_b": 1})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    return {
        "match_id": match["id"],
        "status": match.get("status", "upcoming"),
        "live_score": match.get("live_score"),
        "team_a": match.get("team_a", {}),
        "team_b": match.get("team_b", {})
    }


@router.get(
    "/{match_id}/contests",
    summary="Get match contests",
    description="Get all contests for a match"
)
async def get_match_contests(
    match_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    status_filter: Optional[str] = Query(default=None, alias="status")
):
    # Verify match exists
    match = await db.matches.find_one({"id": match_id}, {"_id": 0, "id": 1})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    query = {"match_id": match_id}
    if status_filter:
        query["status"] = status_filter

    cursor = db.contests.find(query, {"_id": 0}).sort("entry_fee", 1)
    contests = await cursor.to_list(length=50)

    return {"match_id": match_id, "contests": contests, "total": len(contests)}


# ==================== ADMIN ENDPOINTS ====================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create match (Admin)",
    description="Create a new match manually"
)
async def create_match(
    data: MatchCreate,
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    now = utc_now().isoformat()
    match = {
        "id": generate_id(),
        "team_a": data.team_a.model_dump(),
        "team_b": data.team_b.model_dump(),
        "match_type": data.match_type,
        "venue": data.venue,
        "start_time": data.start_time,
        "tournament": data.tournament,
        "status": "upcoming",
        "live_score": None,
        "templates_assigned": [data.template_id] if data.template_id else [],
        "external_match_id": None,
        "created_at": now,
        "updated_at": now
    }
    await db.matches.insert_one(match)
    del match["_id"]
    return match


@router.put(
    "/{match_id}/status",
    summary="Update match status (Admin)"
)
async def update_match_status(
    match_id: str,
    data: MatchStatusUpdate,
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    existing = await db.matches.find_one({"id": match_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Match not found")

    await db.matches.update_one(
        {"id": match_id},
        {"$set": {"status": data.status.value, "updated_at": utc_now().isoformat()}}
    )
    updated = await db.matches.find_one({"id": match_id}, {"_id": 0})
    return updated


@router.put(
    "/{match_id}/live-score",
    summary="Update live score (Admin/Scraper)"
)
async def update_live_score(
    match_id: str,
    data: LiveScoreUpdate,
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    existing = await db.matches.find_one({"id": match_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Match not found")

    await db.matches.update_one(
        {"id": match_id},
        {"$set": {
            "live_score": data.model_dump(),
            "status": "live",
            "updated_at": utc_now().isoformat()
        }}
    )
    return {"match_id": match_id, "score_updated": True}


@router.post(
    "/{match_id}/assign-template",
    summary="Assign template to match (Admin)"
)
async def assign_template(
    match_id: str,
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db),
    template_id: str = Query(...)
):
    match = await db.matches.find_one({"id": match_id})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    template = await db.templates.find_one({"id": template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    await db.matches.update_one(
        {"id": match_id},
        {"$addToSet": {"templates_assigned": template_id}, "$set": {"updated_at": utc_now().isoformat()}}
    )
    return {"match_id": match_id, "template_id": template_id, "assigned": True}
