"""
IPL & Cricket Data Router
Public endpoints powered by CricketData.org APIs (LOT1-5).
IPL Points Table, Live Ticker, Schedule, Player Info.
"""
import logging
from fastapi import APIRouter, Query
from services.cricket_data import cricket_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cricket", tags=["Cricket Data"])

IPL_SERIES_ID = "87c62aac-bc3c-4738-ab93-19da0690488f"


@router.get(
    "/ipl/points-table",
    summary="IPL Points Table — team standings (LOT3 API 3)"
)
async def get_ipl_points_table():
    """Team standings: matches, wins, losses, ties, NR. Cached 30 min."""
    data = await cricket_service.get_series_points(IPL_SERIES_ID)
    if not data:
        return {"error": "Could not fetch points table", "teams": []}
    return {"series_id": IPL_SERIES_ID, "teams": data}


@router.get(
    "/ipl/schedule",
    summary="Full IPL 2026 schedule — 74 matches (LOT2 API 4)"
)
async def get_ipl_schedule():
    """Full IPL match schedule from series_info. Cached 1 hour."""
    data = await cricket_service.get_series_info(IPL_SERIES_ID)
    if not data:
        return {"error": "Could not fetch schedule", "info": None, "matches": []}
    return {
        "info": data.get("info", {}),
        "matches": data.get("matchList", [])
    }


@router.get(
    "/live-ticker",
    summary="Lightweight live scores — all IPL matches (LOT1 API 2)"
)
async def get_live_ticker(ipl_only: bool = Query(default=True)):
    """cricScore feed: ms=fixture/result/live. Cached 60s."""
    data = await cricket_service.get_cric_score()
    if not data:
        return {"scores": [], "error": "Could not fetch live scores"}

    if ipl_only:
        data = [m for m in data if "indian premier league" in (m.get("series", "") or "").lower()]

    scores = []
    for m in data:
        scores.append({
            "id": m.get("id", ""),
            "t1": m.get("t1", ""),
            "t2": m.get("t2", ""),
            "t1s": m.get("t1s", ""),
            "t2s": m.get("t2s", ""),
            "t1img": m.get("t1img", ""),
            "t2img": m.get("t2img", ""),
            "status": m.get("status", ""),
            "ms": m.get("ms", ""),
            "dateTimeGMT": m.get("dateTimeGMT", ""),
        })

    return {"scores": scores, "count": len(scores)}


@router.get(
    "/ipl/squads",
    summary="All IPL team squads — 10 teams (LOT5 API 3)"
)
async def get_ipl_squads():
    """All IPL team squads with player details. Cached 1 hour. ~53KB."""
    data = await cricket_service.get_series_squad(IPL_SERIES_ID)
    if not data:
        return {"error": "Could not fetch squads", "teams": []}
    return {"series_id": IPL_SERIES_ID, "teams": data}


@router.get(
    "/player/{player_id}",
    summary="Player profile + career stats (LOT5 API 1)"
)
async def get_player_profile(player_id: str):
    """Full player info: role, batting/bowling style, career stats by format."""
    data = await cricket_service.get_player_info(player_id)
    if not data:
        return {"error": "Could not fetch player info", "player": None}

    # Clean stats (trim whitespace from values)
    stats = data.get("stats", [])
    cleaned_stats = []
    for s in stats:
        cleaned_stats.append({
            "fn": s.get("fn", "").strip(),
            "matchtype": s.get("matchtype", "").strip(),
            "stat": s.get("stat", "").strip(),
            "value": s.get("value", "").strip(),
        })

    return {
        "player": {
            "id": data.get("id", ""),
            "name": data.get("name", ""),
            "role": data.get("role", ""),
            "battingStyle": data.get("battingStyle", ""),
            "bowlingStyle": data.get("bowlingStyle", ""),
            "country": data.get("country", ""),
            "playerImg": data.get("playerImg", ""),
            "placeOfBirth": data.get("placeOfBirth", ""),
        },
        "stats": cleaned_stats
    }
