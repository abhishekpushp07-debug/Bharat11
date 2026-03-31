"""
Match Router
Handles match listing, details, and live score endpoints for users.
Admin endpoints for match creation and management.
Auto-contest creation on match create / go-live.
"""
import logging
from datetime import timedelta, datetime, timezone

from fastapi import APIRouter, Depends, Query, HTTPException, status, Request
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
    "/{match_id}/scorecard",
    summary="Get detailed scorecard for a match (public)",
    description="Returns full batting/bowling/catching stats from CricketData.org"
)
async def get_match_scorecard_public(
    match_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Public scorecard endpoint — no admin required. Uses MongoDB cache."""
    from services.api_cache import cached_cricket
    from services.settlement_engine import parse_scorecard_to_metrics, _auto_link_cricketdata_id

    match = await db.matches.find_one({"id": match_id}, {"_id": 0})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    cd_id = match.get("cricketdata_id") or match.get("external_match_id", "")
    if not cd_id:
        cd_id = await _auto_link_cricketdata_id(match, db)
    if not cd_id:
        return {"match_id": match_id, "error": "Scorecard not available", "scorecard": None}

    data = await cached_cricket.get_scorecard(db, cd_id)
    if not data:
        return {"match_id": match_id, "error": "Could not fetch scorecard", "scorecard": None}

    metrics = parse_scorecard_to_metrics(data)

    return {
        "match_id": match_id,
        "match_name": data.get("name", ""),
        "venue": data.get("venue", ""),
        "date": data.get("date", ""),
        "status": data.get("status", ""),
        "teams": data.get("teams", []),
        "toss_winner": data.get("tossWinner", ""),
        "toss_choice": data.get("tossChoice", ""),
        "match_winner": data.get("matchWinner", ""),
        "score_summary": data.get("score", []),
        "scorecard": data.get("scorecard", []),
        "metrics": metrics,
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


# ==================== NEW PLAYER APIs (LOT1-5) ====================

IPL_SERIES_ID = "87c62aac-bc3c-4738-ab93-19da0690488f"


@router.get(
    "/{match_id}/squad",
    summary="Get playing squad for a match (LOT5 API 2)"
)
async def get_match_squad(match_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Returns both teams with player details. Uses MongoDB cache."""
    from services.api_cache import cached_cricket
    from services.settlement_engine import _auto_link_cricketdata_id

    match = await db.matches.find_one({"id": match_id}, {"_id": 0})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    cd_id = match.get("cricketdata_id") or match.get("external_match_id", "")
    if not cd_id:
        cd_id = await _auto_link_cricketdata_id(match, db)
    if not cd_id:
        return {"match_id": match_id, "error": "Squad not available", "squads": []}

    data = await cached_cricket.get_squad(db, cd_id)
    if not data:
        return {"match_id": match_id, "error": "Could not fetch squad", "squads": []}

    return {"match_id": match_id, "squads": data}


@router.get(
    "/{match_id}/fantasy-points",
    summary="Get fantasy points per player (LOT3 API 2)"
)
async def get_match_fantasy_points(match_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Player fantasy points by innings + totals. SLOW API - cached in MongoDB."""
    from services.api_cache import cached_cricket
    from services.settlement_engine import _auto_link_cricketdata_id

    match = await db.matches.find_one({"id": match_id}, {"_id": 0})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    cd_id = match.get("cricketdata_id") or match.get("external_match_id", "")
    if not cd_id:
        cd_id = await _auto_link_cricketdata_id(match, db)
    if not cd_id:
        return {"match_id": match_id, "error": "Fantasy points not available", "innings": [], "totals": []}

    data = await cached_cricket.get_match_points(db, cd_id)
    if not data:
        return {"match_id": match_id, "error": "Could not fetch points", "innings": [], "totals": []}

    return {
        "match_id": match_id,
        "innings": data.get("innings", []),
        "totals": data.get("totals", [])
    }


@router.get(
    "/{match_id}/match-info",
    summary="Get detailed match info - toss, winner (LOT2 API 5)"
)
async def get_match_info_detail(match_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Returns toss winner/choice, match winner, series_id, scores. Uses MongoDB cache."""
    from services.api_cache import cached_cricket
    from services.settlement_engine import _auto_link_cricketdata_id

    match = await db.matches.find_one({"id": match_id}, {"_id": 0})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    cd_id = match.get("cricketdata_id") or match.get("external_match_id", "")
    if not cd_id:
        cd_id = await _auto_link_cricketdata_id(match, db)
    if not cd_id:
        return {"match_id": match_id, "error": "Info not available"}

    data = await cached_cricket.get_match_info(db, cd_id)
    if not data:
        return {"match_id": match_id, "error": "Could not fetch info"}

    return {
        "match_id": match_id,
        "name": data.get("name", ""),
        "venue": data.get("venue", ""),
        "date": data.get("date", ""),
        "status": data.get("status", ""),
        "toss_winner": data.get("tossWinner", ""),
        "toss_choice": data.get("tossChoice", ""),
        "match_winner": data.get("matchWinner", ""),
        "score": data.get("score", []),
        "teams": data.get("teams", []),
        "team_info": data.get("teamInfo", []),
    }


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



# ==================== LIVE CRICKET DATA (Unified) ====================

@router.get(
    "/live/cricket",
    summary="Fetch live matches from Cricbuzz + CricketData.org fallback"
)
async def get_live_cricket(ipl_only: bool = Query(default=False)):
    from services.cricket_data import cricket_service
    data = await cricket_service.get_live_matches(ipl_only=ipl_only)
    return data


@router.get(
    "/live/status",
    summary="Get cricket data service status"
)
async def get_cricket_status():
    from services.cricket_data import cricket_service
    return cricket_service.get_status()


@router.post(
    "/live/sync",
    summary="Sync live matches to DB (Admin) - auto creates matches + contests"
)
async def sync_live_matches(
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db),
    ipl_only: bool = Query(default=True)
):
    from services.cricket_data import cricket_service

    data = await cricket_service.get_live_matches(ipl_only=ipl_only)
    live_matches = data.get("matches", [])

    if not live_matches:
        return {
            "synced": 0,
            "source": data.get("source", "none"),
            "message": "No matches found from any source"
        }

    created = 0
    updated = 0
    contests_created = 0
    now = utc_now().isoformat()

    for lm in live_matches:
        source_id = lm.get("source_id", "")
        if not source_id:
            continue

        # Check if already exists (by external_match_id OR cricketdata_id to prevent duplicates)
        existing = await db.matches.find_one(
            {"$or": [
                {"external_match_id": source_id},
                {"cricketdata_id": source_id},
            ]},
            {"_id": 0}
        )

        if existing:
            # Update status if changed
            new_status = lm.get("status", "upcoming")
            old_status = existing.get("status", "upcoming")
            updates = {"updated_at": now, "status_text": lm.get("status_text", "")}

            if new_status != old_status:
                VALID = {"upcoming": ["live", "completed"], "live": ["completed"]}
                if new_status in VALID.get(old_status, []):
                    updates["status"] = new_status

            # Update scores if available
            if lm.get("scores"):
                updates["live_score"] = {"scores": lm["scores"], "updated_at": now}

            await db.matches.update_one(
                {"external_match_id": source_id}, {"$set": updates}
            )
            updated += 1

            # Auto-contest on status change to live
            if updates.get("status") == "live":
                contest_count = await db.contests.count_documents({"match_id": existing["id"]})
                if contest_count == 0:
                    match_data = await db.matches.find_one({"id": existing["id"]}, {"_id": 0})
                    ac = await _auto_create_contest(db, match_data)
                    if ac:
                        contests_created += 1
        else:
            # Before creating — also check by team short_names to prevent duplicates
            team_a = lm.get("team_a", {})
            team_b = lm.get("team_b", {})
            ta_short = team_a.get("short_name", "")
            tb_short = team_b.get("short_name", "")
            if ta_short and tb_short:
                team_match = await db.matches.find_one({
                    "team_a.short_name": {"$in": [ta_short, tb_short]},
                    "team_b.short_name": {"$in": [ta_short, tb_short]},
                }, {"_id": 0, "id": 1})
                if team_match:
                    # Link cricketdata_id to existing match instead of creating duplicate
                    await db.matches.update_one(
                        {"id": team_match["id"]},
                        {"$set": {"cricketdata_id": source_id, "external_match_id": source_id, "updated_at": now}}
                    )
                    updated += 1
                    continue

            # Create new match
            start_time = lm.get("date", now)

            match = {
                "id": generate_id(),
                "external_match_id": source_id,
                "cricketdata_id": source_id if lm.get("source") == "cricketdata" else None,
                "source": lm.get("source", "unknown"),
                "team_a": team_a,
                "team_b": team_b,
                "match_type": lm.get("match_type", "T20"),
                "venue": lm.get("venue", ""),
                "start_time": start_time,
                "status": lm.get("status", "upcoming"),
                "status_text": lm.get("status_text", ""),
                "live_score": {"scores": lm.get("scores", []), "updated_at": now} if lm.get("scores") else None,
                "templates_assigned": [],
                "created_at": now,
                "updated_at": now
            }
            await db.matches.insert_one(match)
            del match["_id"]
            created += 1

            # Auto-create contest for new match
            ac = await _auto_create_contest(db, match)
            if ac:
                contests_created += 1

    return {
        "source": data.get("source", "none"),
        "total_from_source": len(live_matches),
        "created": created,
        "updated": updated,
        "contests_auto_created": contests_created,
        "synced": created + updated,
    }


@router.post(
    "/live/sync-ipl-schedule",
    summary="Sync FULL IPL 2026 schedule from series_info API (1 call = 70 matches)"
)
async def sync_ipl_schedule(
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Master sync: Fetches entire IPL 2026 schedule from CricketData.org series_info API.
    - Creates new matches with proper cricketdata_id
    - Updates existing matches (status, scores, cricketdata_id)
    - Auto-links orphan matches by team name matching
    - Auto-creates contests for upcoming/live matches
    Uses 1 API call only.
    """
    from services.api_cache import cached_cricket
    from services.cricket_data import cricket_service, _get_short_name, _align_team_info, IPL_SHORT_NAMES

    IPL_SERIES_ID = "87c62aac-bc3c-4738-ab93-19da0690488f"

    # Fetch full schedule (uses MongoDB cache if available)
    series_data = await cached_cricket.get_series_info(db, IPL_SERIES_ID)
    if not series_data:
        return {"error": "Could not fetch IPL schedule from API", "synced": 0}

    match_list = series_data.get("matchList", [])
    series_info = series_data.get("info", {})
    now = utc_now().isoformat()

    created = 0
    updated = 0
    linked = 0
    contests_created = 0
    errors = []

    for api_match in match_list:
        cd_id = api_match.get("id", "")
        if not cd_id:
            continue

        teams = api_match.get("teams", [])
        team_info = api_match.get("teamInfo", [])
        match_started = api_match.get("matchStarted", False)
        match_ended = api_match.get("matchEnded", False)

        if match_ended:
            m_status = "completed"
        elif match_started:
            m_status = "live"
        else:
            m_status = "upcoming"

        # ALIGN teamInfo to teams[] order (fixes random API swap bug)
        if len(team_info) >= 2 and len(teams) >= 2:
            team_a_info, team_b_info = _align_team_info(teams, team_info)
            t1_name = team_a_info.get("name", teams[0])
            t1_short = _get_short_name(team_a_info.get("shortname", t1_name))
            t1_img = team_a_info.get("img", "")
            t2_name = team_b_info.get("name", teams[1])
            t2_short = _get_short_name(team_b_info.get("shortname", t2_name))
            t2_img = team_b_info.get("img", "")
        else:
            t1_name = teams[0] if len(teams) > 0 else "?"
            t2_name = teams[1] if len(teams) > 1 else "?"
            t1_short = _get_short_name(t1_name)
            t2_short = _get_short_name(t2_name)
            t1_img = ""
            t2_img = ""

        # Scores from API
        scores = []
        for s in api_match.get("score", []):
            scores.append({
                "inning": s.get("inning", ""),
                "r": s.get("r", 0),
                "w": s.get("w", 0),
                "o": s.get("o", 0),
                "runs": s.get("r", 0),
                "wickets": s.get("w", 0),
                "overs": s.get("o", 0),
            })

        # Check if already exists by cricketdata_id
        existing = await db.matches.find_one(
            {"$or": [
                {"cricketdata_id": cd_id},
                {"external_match_id": cd_id},
            ]},
            {"_id": 0}
        )

        if not existing:
            # Try matching by team names (for matches synced from Cricbuzz without cd_id)
            existing = await db.matches.find_one(
                {
                    "team_a.short_name": {"$in": [t1_short, t2_short]},
                    "team_b.short_name": {"$in": [t1_short, t2_short]},
                    "cricketdata_id": {"$in": [None, "", "NONE"]},
                },
                {"_id": 0}
            )
            if existing:
                # Link cricketdata_id to orphan match
                await db.matches.update_one(
                    {"id": existing["id"]},
                    {"$set": {"cricketdata_id": cd_id, "external_match_id": cd_id}}
                )
                linked += 1

        if existing:
            # Update existing match
            updates = {
                "updated_at": now,
                "status_text": api_match.get("status", ""),
                "venue": api_match.get("venue", existing.get("venue", "")),
                "cricketdata_id": cd_id,
            }

            # Update status (only forward transitions)
            old_status = existing.get("status", "upcoming")
            if m_status != old_status:
                VALID = {"upcoming": ["live", "completed"], "live": ["completed"]}
                if m_status in VALID.get(old_status, []):
                    updates["status"] = m_status

            # Update scores — NEVER overwrite non-zero scores with zeros
            if scores:
                existing_scores = existing.get("live_score", {}).get("scores", [])
                existing_has_real_data = any(s.get("r", 0) > 0 or s.get("runs", 0) > 0 for s in existing_scores)
                new_has_real_data = any(s.get("r", 0) > 0 or s.get("runs", 0) > 0 for s in scores)
                if new_has_real_data or not existing_has_real_data:
                    updates["live_score"] = {"scores": scores, "updated_at": now}

            # Update team images if missing
            if not existing.get("team_a", {}).get("img") and t1_img:
                updates["team_a.img"] = t1_img
            if not existing.get("team_b", {}).get("img") and t2_img:
                updates["team_b.img"] = t2_img

            await db.matches.update_one({"id": existing["id"]}, {"$set": updates})
            updated += 1
        else:
            # Create new match
            match_doc = {
                "id": generate_id(),
                "external_match_id": cd_id,
                "cricketdata_id": cd_id,
                "source": "cricketdata",
                "team_a": {"name": t1_name, "short_name": t1_short, "img": t1_img},
                "team_b": {"name": t2_name, "short_name": t2_short, "img": t2_img},
                "match_type": api_match.get("matchType", "t20"),
                "venue": api_match.get("venue", ""),
                "start_time": api_match.get("dateTimeGMT", now),
                "status": m_status,
                "status_text": api_match.get("status", ""),
                "live_score": {"scores": scores, "updated_at": now} if scores else None,
                "templates_assigned": [],
                "created_at": now,
                "updated_at": now,
            }
            try:
                await db.matches.insert_one(match_doc)
                del match_doc["_id"]
                created += 1

                # Auto-create contest for upcoming/live matches
                ac = await _auto_create_contest(db, match_doc)
                if ac:
                    contests_created += 1
            except Exception as e:
                errors.append(f"Insert failed for {t1_short} vs {t2_short}: {str(e)}")

    return {
        "series": series_info.get("name", "IPL 2026"),
        "total_from_api": len(match_list),
        "created": created,
        "updated": updated,
        "linked_orphans": linked,
        "contests_auto_created": contests_created,
        "synced": created + updated,
        "errors": errors[:5] if errors else [],
    }


@router.post(
    "/{match_id}/sync-score",
    summary="Sync live score for a match"
)
async def sync_match_score(
    match_id: str,
    current_user: AdminUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    from services.cricket_data import cricket_service

    match = await db.matches.find_one({"id": match_id}, {"_id": 0})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    slug = match.get("slug") or match.get("external_match_id")
    if not slug:
        raise HTTPException(status_code=400, detail="No external ID linked")

    score = await cricket_service.get_match_score(slug)
    if not score:
        return {"match_id": match_id, "updated": False, "message": "Could not fetch score"}

    await db.matches.update_one(
        {"id": match_id},
        {"$set": {"live_score": score, "updated_at": utc_now().isoformat()}}
    )

    return {"match_id": match_id, "updated": True, "score": score}



@router.get(
    "/{match_id}/ball-by-ball",
    summary="Ball-by-ball data (LOT4) — extras & events"
)
async def get_match_bbb(match_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Ball-by-ball feed from match_bbb API. Uses MongoDB cache."""
    from services.api_cache import cached_cricket
    from services.settlement_engine import _auto_link_cricketdata_id

    match = await db.matches.find_one({"id": match_id}, {"_id": 0})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    cd_id = match.get("cricketdata_id") or match.get("external_match_id", "")
    if not cd_id:
        cd_id = await _auto_link_cricketdata_id(match, db)
    if not cd_id:
        return {"match_id": match_id, "error": "BBB data not available", "balls": []}

    data = await cached_cricket.get_match_bbb(db, cd_id)
    if not data:
        return {"match_id": match_id, "error": "Could not fetch BBB data", "balls": []}

    bbb = data.get("bbb", [])
    return {
        "match_id": match_id,
        "name": data.get("name", ""),
        "status": data.get("status", ""),
        "balls": bbb,
        "total_events": len(bbb)
    }


@router.get(
    "/{match_id}/ai-commentary",
    summary="AI-powered structured cricket commentary from scorecard"
)
async def get_ai_commentary(match_id: str, force: bool = False, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Generates structured AI commentary. Returns match_pulse, key_moments, star_performers, turning_point, verdict."""
    from services.ai_commentary import generate_ai_commentary

    # Check cache first (unless force refresh)
    if not force:
        cached = await db.commentary_cache.find_one({"match_id": match_id}, {"_id": 0})
        if cached and cached.get("data"):
            return {"match_id": match_id, "cached": True, **cached["data"]}
        # Backwards compat: old cache format
        if cached and cached.get("items"):
            return {"match_id": match_id, "commentary": cached["items"], "cached": True}

    # Get scorecard
    match = await db.matches.find_one({"id": match_id}, {"_id": 0})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    scorecard = None
    cd_id = match.get("cricketdata_id") or match.get("external_match_id", "")
    if cd_id:
        from services.api_cache import cached_cricket
        scorecard = await cached_cricket.get_scorecard(db, cd_id)

    if not scorecard or not scorecard.get("scorecard"):
        return {"match_id": match_id, "commentary": [], "error": "Scorecard not available yet"}

    # Get match info for context
    match_info = None
    if cd_id:
        from services.api_cache import cached_cricket
        match_info = await cached_cricket.get_match_info(db, cd_id)

    # Generate structured AI commentary
    result = await generate_ai_commentary(scorecard, match_info)

    # Cache structured result
    if result:
        await db.commentary_cache.update_one(
            {"match_id": match_id},
            {"$set": {
                "match_id": match_id,
                "data": result,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )

    return {"match_id": match_id, "cached": False, **result}



# ==================== TEMPLATE DEADLINE STATUS ====================

@router.get(
    "/{match_id}/template-deadlines",
    summary="Get deadline status for all templates of a match"
)
async def get_template_deadlines(match_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Returns deadline status (OPEN/LOCKED) for each template assigned to this match.
    Used by frontend to show lock badges and disable submission forms.
    """
    from services.match_engine import check_can_submit, get_deadline_for_template, get_match_current_state

    match = await db.matches.find_one({"id": match_id}, {"_id": 0})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    template_ids = match.get("templates_assigned", [])
    if not template_ids:
        return {"match_id": match_id, "templates": [], "current_state": {}}

    templates = await db.templates.find(
        {"id": {"$in": template_ids}},
        {"_id": 0}
    ).to_list(length=10)

    state = await get_match_current_state(match_id, db)
    results = []

    for t in templates:
        deadline = get_deadline_for_template(t)
        can = await check_can_submit(t, match_id, db)
        results.append({
            "template_id": t["id"],
            "template_name": t.get("name", ""),
            "template_type": t.get("template_type", ""),
            "phase_label": t.get("phase_label", ""),
            "innings_range": t.get("innings_range", []),
            "over_start": t.get("over_start"),
            "over_end": t.get("over_end"),
            "deadline_innings": deadline["innings"],
            "deadline_over": deadline["over"],
            "is_locked": not can["can_submit"],
            "status": "LOCKED" if not can["can_submit"] else "OPEN",
            "reason": can["reason"],
            "question_count": len(t.get("question_ids", [])),
            "total_points": t.get("total_points", 0),
        })

    return {
        "match_id": match_id,
        "current_state": state,
        "templates": results
    }



# ==================== MOOD METER (Live Poll) ====================

class MoodVoteRequest(BaseModel):
    team: str = Field(..., description="Team short_name to vote for (e.g. CSK, MI)")

@router.post("/{match_id}/mood-vote", summary="Cast a mood vote for which team will win")
async def cast_mood_vote(
    match_id: str,
    body: MoodVoteRequest,
    user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Users vote for which team they think will win. One vote per user per match."""
    match = await db.matches.find_one({"id": match_id}, {"_id": 0, "team_a": 1, "team_b": 1, "status": 1})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    team_a_short = match.get("team_a", {}).get("short_name", "")
    team_b_short = match.get("team_b", {}).get("short_name", "")
    valid_teams = [team_a_short, team_b_short]

    if body.team not in valid_teams:
        raise HTTPException(status_code=400, detail=f"Invalid team. Choose from: {valid_teams}")

    user_id = user.id

    # Upsert: one vote per user per match
    await db.mood_votes.update_one(
        {"match_id": match_id, "user_id": user_id},
        {"$set": {
            "match_id": match_id,
            "user_id": user_id,
            "team": body.team,
            "voted_at": utc_now(),
        }},
        upsert=True
    )

    # Get updated counts
    pipeline = [
        {"$match": {"match_id": match_id}},
        {"$group": {"_id": "$team", "count": {"$sum": 1}}}
    ]
    agg = await db.mood_votes.aggregate(pipeline).to_list(10)
    counts = {r["_id"]: r["count"] for r in agg}
    total = sum(counts.values()) or 1

    return {
        "success": True,
        "your_vote": body.team,
        "team_a": team_a_short,
        "team_b": team_b_short,
        "team_a_votes": counts.get(team_a_short, 0),
        "team_b_votes": counts.get(team_b_short, 0),
        "team_a_pct": round(counts.get(team_a_short, 0) / total * 100),
        "team_b_pct": round(counts.get(team_b_short, 0) / total * 100),
        "total_votes": total,
    }


@router.get("/{match_id}/mood-meter", summary="Get current mood meter results")
async def get_mood_meter(
    match_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get live mood meter votes for a match. Public endpoint."""
    match = await db.matches.find_one({"id": match_id}, {"_id": 0, "team_a": 1, "team_b": 1})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    team_a_short = match.get("team_a", {}).get("short_name", "")
    team_b_short = match.get("team_b", {}).get("short_name", "")

    pipeline = [
        {"$match": {"match_id": match_id}},
        {"$group": {"_id": "$team", "count": {"$sum": 1}}}
    ]
    agg = await db.mood_votes.aggregate(pipeline).to_list(10)
    counts = {r["_id"]: r["count"] for r in agg}
    total = sum(counts.values()) or 1

    # Try to check if current user has voted (optional auth)
    user_vote = None
    try:
        auth = request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            from core.security import JWTManager
            token = auth.split(" ", 1)[1]
            payload = JWTManager.decode_token(token)
            if payload:
                user_id = payload.get("sub", "")
                if user_id:
                    vote_doc = await db.mood_votes.find_one({"match_id": match_id, "user_id": user_id}, {"_id": 0, "team": 1})
                    if vote_doc:
                        user_vote = vote_doc["team"]
    except Exception as e:
        logger.warning(f"Mood meter user check failed: {e}")

    return {
        "match_id": match_id,
        "team_a": team_a_short,
        "team_b": team_b_short,
        "team_a_votes": counts.get(team_a_short, 0),
        "team_b_votes": counts.get(team_b_short, 0),
        "team_a_pct": round(counts.get(team_a_short, 0) / total * 100),
        "team_b_pct": round(counts.get(team_b_short, 0) / total * 100),
        "total_votes": total,
        "user_vote": user_vote,
    }
