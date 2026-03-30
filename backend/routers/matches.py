"""
Match Router
Handles match listing, details, and live score endpoints for users.
Admin endpoints for match creation and management.
Auto-contest creation on match create / go-live.
"""
import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Annotated, Optional
from pydantic import BaseModel, Field

from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import get_db
from core.dependencies import CurrentUser, AdminUser
from models.schemas import MatchStatus, generate_id, utc_now

logger = logging.getLogger(__name__)

DEFAULT_ENTRY_FEE = 1000

router = APIRouter(prefix="/matches", tags=["Matches"])


# ==================== AUTO-CONTEST HELPER ====================

async def _auto_create_contest(db, match: dict) -> dict | None:
    """
    Auto-create a contest for a match using default template.
    Prize: 50% 1st, 30% 2nd, 20% 3rd of total pool.
    Entry fee: 1000 coins.
    Returns contest dict or None if no template available.
    """
    match_id = match.get("id")
    if not match_id:
        return None

    # Check if contest already exists
    existing = await db.contests.count_documents({"match_id": match_id})
    if existing > 0:
        return None

    # Get template - prefer assigned, fallback to default
    template = None
    templates_assigned = match.get("templates_assigned", [])
    if templates_assigned:
        template = await db.templates.find_one(
            {"id": templates_assigned[0], "is_active": True}, {"_id": 0}
        )

    if not template:
        template = await db.templates.find_one(
            {"template_type": "full_match", "is_default": True, "is_active": True},
            {"_id": 0}
        )
    if not template:
        template = await db.templates.find_one(
            {"is_active": True}, {"_id": 0}
        )
    if not template:
        return None

    # Build contest name
    team_a = match.get("team_a", {}).get("short_name", "Team A")
    team_b = match.get("team_b", {}).get("short_name", "Team B")
    contest_name = f"{team_a} vs {team_b} - Mega Contest"

    from datetime import datetime as dt
    start_time = match.get("start_time", "")
    if isinstance(start_time, str):
        try:
            start_time = dt.fromisoformat(start_time.replace('Z', '+00:00'))
        except Exception:
            start_time = utc_now() + timedelta(hours=1)

    now = utc_now().isoformat()
    contest = {
        "id": generate_id(),
        "match_id": match_id,
        "template_id": template["id"],
        "name": contest_name,
        "entry_fee": DEFAULT_ENTRY_FEE,
        "prize_pool": 0,
        "max_participants": 1000,
        "current_participants": 0,
        "prize_distribution": [],
        "status": "open",
        "lock_time": (start_time - timedelta(minutes=5)).isoformat() if hasattr(start_time, 'isoformat') else start_time,
        "auto_created": True,
        "created_at": now,
        "updated_at": now
    }
    await db.contests.insert_one(contest)
    del contest["_id"]

    # Auto-assign template to match
    if template["id"] not in templates_assigned:
        templates_assigned.append(template["id"])
        await db.matches.update_one(
            {"id": match_id},
            {"$set": {"templates_assigned": templates_assigned}}
        )

    logger.info(f"Auto-created contest '{contest_name}' for match {match_id} with template {template['name']}")
    return contest


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
    current_user: AdminUser,
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

    # AUTO-CONTEST: Create contest with default template
    auto_contest = await _auto_create_contest(db, match)
    if auto_contest:
        match["auto_contest_created"] = auto_contest["name"]

    return match


@router.put(
    "/{match_id}/status",
    summary="Update match status (Admin)"
)
async def update_match_status(
    match_id: str,
    data: MatchStatusUpdate,
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    existing = await db.matches.find_one({"id": match_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Match not found")

    # Validate status transitions
    VALID_TRANSITIONS = {
        "upcoming": ["live", "cancelled", "abandoned"],
        "live": ["completed", "abandoned"],
        "completed": [],  # Terminal state
        "cancelled": [],  # Terminal state
        "abandoned": [],  # Terminal state
    }
    current_status = existing.get("status", "upcoming")
    new_status = data.status.value
    allowed = VALID_TRANSITIONS.get(current_status, [])
    if new_status not in allowed and current_status != new_status:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition: {current_status} -> {new_status}. Allowed: {allowed}"
        )

    await db.matches.update_one(
        {"id": match_id},
        {"$set": {"status": new_status, "updated_at": utc_now().isoformat()}}
    )

    # AUTO-CONTEST: When match goes live, ensure it has a contest
    if new_status == "live":
        existing_contests = await db.contests.count_documents({"match_id": match_id})
        if existing_contests == 0:
            # Auto-assign default template if none assigned
            templates_assigned = existing.get("templates_assigned", [])
            if not templates_assigned:
                default_template = await db.templates.find_one(
                    {"template_type": "full_match", "is_default": True, "is_active": True},
                    {"_id": 0}
                )
                if not default_template:
                    default_template = await db.templates.find_one(
                        {"template_type": "full_match", "is_active": True},
                        {"_id": 0}
                    )
                if default_template:
                    await db.matches.update_one(
                        {"id": match_id},
                        {"$set": {"templates_assigned": [default_template["id"]]}}
                    )
                    logger.info(f"Auto-assigned default template {default_template['name']} to match {match_id}")

            match_data = await db.matches.find_one({"id": match_id}, {"_id": 0})
            auto_contest = await _auto_create_contest(db, match_data)
            if auto_contest:
                logger.info(f"Auto-created contest '{auto_contest['name']}' for live match {match_id}")

    updated = await db.matches.find_one({"id": match_id}, {"_id": 0})
    return updated


@router.put(
    "/{match_id}/live-score",
    summary="Update live score (Admin/Scraper)"
)
async def update_live_score(
    match_id: str,
    data: LiveScoreUpdate,
    current_user: AdminUser,
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
    current_user: AdminUser,
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



# ==================== LIVE CRICKET DATA (Cricbuzz) ====================

@router.get(
    "/live/cricbuzz",
    summary="Fetch live matches from Cricbuzz",
    description="Returns real-time match data from Cricbuzz. Free, 2-ball delay."
)
async def get_cricbuzz_live():
    from services.cricket_data import cricket_data_service
    matches = await cricket_data_service.fetch_live_matches()
    return {
        "source": "cricbuzz",
        "connected": cricket_data_service.is_connected,
        "matches": matches,
        "total": len(matches)
    }


@router.post(
    "/live/sync",
    summary="Sync live matches from Cricbuzz to DB (Admin)",
    description="Fetch matches from Cricbuzz and create/update them in our database"
)
async def sync_cricbuzz_matches(
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    from services.cricket_data import cricket_data_service

    cb_matches = await cricket_data_service.fetch_live_matches()
    if not cb_matches:
        return {"synced": 0, "message": "No matches from Cricbuzz (might be offline)"}

    created = 0
    updated = 0
    now = utc_now().isoformat()

    for cb in cb_matches:
        cricbuzz_id = cb.get("cricbuzz_id", "")
        if not cricbuzz_id:
            continue

        existing = await db.matches.find_one(
            {"external_match_id": cricbuzz_id},
            {"_id": 0, "id": 1}
        )

        if existing:
            # Update status
            await db.matches.update_one(
                {"external_match_id": cricbuzz_id},
                {"$set": {
                    "status": cb["status"],
                    "updated_at": now
                }}
            )
            updated += 1
        else:
            # Create new match
            match = {
                "id": generate_id(),
                "external_match_id": cricbuzz_id,
                "team_a": cb["team_a"],
                "team_b": cb["team_b"],
                "match_type": cb.get("match_type", "T20"),
                "venue": cb.get("venue", ""),
                "start_time": now,
                "tournament": cb.get("series", ""),
                "status": cb["status"],
                "live_score": None,
                "templates_assigned": [],
                "created_at": now,
                "updated_at": now
            }
            await db.matches.insert_one(match)
            created += 1

    return {
        "synced": created + updated,
        "created": created,
        "updated": updated,
        "source_matches": len(cb_matches),
        "connected": cricket_data_service.is_connected
    }


@router.post(
    "/{match_id}/sync-score",
    summary="Sync live score from Cricbuzz for a match",
    description="Pull latest score from Cricbuzz and update match live_score"
)
async def sync_match_score(
    match_id: str,
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    from services.cricket_data import cricket_data_service

    match = await db.matches.find_one({"id": match_id}, {"_id": 0})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    cricbuzz_id = match.get("external_match_id")
    if not cricbuzz_id:
        raise HTTPException(status_code=400, detail="No Cricbuzz ID linked to this match")

    score = await cricket_data_service.fetch_live_score(cricbuzz_id)
    if not score:
        return {"match_id": match_id, "updated": False, "message": "Could not fetch score"}

    await db.matches.update_one(
        {"id": match_id},
        {"$set": {
            "live_score": score,
            "status": "live",
            "updated_at": utc_now().isoformat()
        }}
    )

    return {
        "match_id": match_id,
        "updated": True,
        "score": score
    }
