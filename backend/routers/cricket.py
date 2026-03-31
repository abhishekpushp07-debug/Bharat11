"""
IPL & Cricket Data Router
Public endpoints powered by CricketData.org APIs (LOT1-5).
ALL API calls go through MongoDB cache layer — no duplicate API hits.
IPL Points Table, Live Ticker, Schedule, Player Info, Team Drill-Down.
"""
import logging
from fastapi import APIRouter, Query, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import get_db
from services.api_cache import cached_cricket
from services.cricket_data import cricket_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cricket", tags=["Cricket Data"])

IPL_SERIES_ID = "87c62aac-bc3c-4738-ab93-19da0690488f"


@router.get(
    "/ipl/points-table",
    summary="IPL Points Table — team standings (LOT3 API 3)"
)
async def get_ipl_points_table(db: AsyncIOMotorDatabase = Depends(get_db)):
    """Team standings: matches, wins, losses, ties, NR. Redis 5min + MongoDB cache."""
    from services.redis_cache import cache_get, cache_set, CacheTTL
    cached = await cache_get("points_table")
    if cached:
        return cached

    from services.cricket_data import _get_short_name
    data = await cached_cricket.get_series_points(db, IPL_SERIES_ID)
    if not data:
        return {"error": "Could not fetch points table", "teams": []}
    for team in data:
        sn = team.get("shortname", "")
        team["shortname"] = _get_short_name(sn)
    result = {"series_id": IPL_SERIES_ID, "teams": data}
    await cache_set("points_table", result, CacheTTL.POINTS_TABLE)
    return result


@router.get(
    "/ipl/schedule",
    summary="Full IPL 2026 schedule — 74 matches (LOT2 API 4)"
)
async def get_ipl_schedule(db: AsyncIOMotorDatabase = Depends(get_db)):
    """Full IPL match schedule from series_info. Cached in MongoDB."""
    data = await cached_cricket.get_series_info(db, IPL_SERIES_ID)
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
async def get_live_ticker(
    ipl_only: bool = Query(default=True),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """cricScore feed: ms=fixture/result/live. Cached 45s in MongoDB + 30s in Redis."""
    from services.redis_cache import cache_get, cache_set, CacheTTL
    cache_key = f"live_ticker:ipl={ipl_only}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    data = await cached_cricket.get_cric_score(db)
    if not data:
        return {"scores": [], "error": "Could not fetch live scores"}

    if ipl_only:
        data = [m for m in data if "indian premier league" in (m.get("series", "") or "").lower()]

    scores = []
    from datetime import timedelta
    IST_OFFSET = timedelta(hours=5, minutes=30)
    for m in data:
        # Convert status text from GMT to IST
        status_text = m.get("status", "")
        date_gmt = m.get("dateTimeGMT", "")
        
        # Build IST display from dateTimeGMT
        ist_display = ""
        if date_gmt:
            try:
                from dateutil.parser import parse as dt_parse
                from datetime import timezone as tz
                dt_obj = dt_parse(str(date_gmt))
                if dt_obj.tzinfo is None:
                    dt_obj = dt_obj.replace(tzinfo=tz.utc)
                ist_dt = dt_obj + IST_OFFSET
                ist_display = ist_dt.strftime("%d %b, %I:%M %p") + " IST"
            except Exception:
                ist_display = date_gmt

        # Replace GMT time in status with IST
        if "GMT" in status_text and ist_display:
            import re
            status_text = re.sub(
                r'at\s+\w+\s+\d+,\s+\d+:\d+\s+GMT',
                f'at {ist_display}',
                status_text
            )
            if "GMT" in status_text:
                status_text = status_text.replace("GMT", "IST")

        scores.append({
            "id": m.get("id", ""),
            "t1": m.get("t1", ""),
            "t2": m.get("t2", ""),
            "t1s": m.get("t1s", ""),
            "t2s": m.get("t2s", ""),
            "t1img": m.get("t1img", ""),
            "t2img": m.get("t2img", ""),
            "status": status_text,
            "ms": m.get("ms", ""),
            "dateTimeGMT": date_gmt,
            "ist_display": ist_display,
        })

    result = {"scores": scores, "count": len(scores)}
    await cache_set(cache_key, result, CacheTTL.LIVE_TICKER)
    return result


@router.get(
    "/ipl/squads",
    summary="All IPL team squads — 10 teams (LOT5 API 3)"
)
async def get_ipl_squads(db: AsyncIOMotorDatabase = Depends(get_db)):
    """All IPL team squads with player details. Cached permanently in MongoDB."""
    data = await cached_cricket.get_series_squad(db, IPL_SERIES_ID)
    if not data:
        return {"error": "Could not fetch squads", "teams": []}
    return {"series_id": IPL_SERIES_ID, "teams": data}


@router.get(
    "/player/{player_id}",
    summary="Player profile + career stats (LOT5 API 1)"
)
async def get_player_profile(player_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Full player info: role, batting/bowling style, career stats by format."""
    data = await cached_cricket.get_player_info(db, player_id)
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


# ==================== TEAM DRILL-DOWN ====================

@router.get(
    "/ipl/team/{team_short}/matches",
    summary="Get all IPL matches for a specific team"
)
async def get_team_matches(
    team_short: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Returns all IPL 2026 matches involving the specified team.
    Data from series_info (cached), enriched with scores from cricScore.
    """
    team_short_upper = team_short.upper()

    # Get full IPL schedule from cache/API
    series_data = await cached_cricket.get_series_info(db, IPL_SERIES_ID)
    if not series_data:
        return {"team": team_short_upper, "matches": [], "error": "Could not fetch schedule"}

    all_matches = series_data.get("matchList", [])

    # Normalize team names for matching
    team_aliases = _get_team_aliases(team_short_upper)

    team_matches = []
    for m in all_matches:
        teams = m.get("teams", [])
        team_info = m.get("teamInfo", [])
        name = m.get("name", "")

        # Check if this team is playing
        is_team_match = False
        for t in teams:
            if any(alias.lower() in t.lower() for alias in team_aliases):
                is_team_match = True
                break
        if not is_team_match:
            for ti in team_info:
                sn = (ti.get("shortname", "") or "").upper()
                if sn == team_short_upper or sn in team_aliases:
                    is_team_match = True
                    break

        if is_team_match:
            team_matches.append({
                "id": m.get("id", ""),
                "name": m.get("name", ""),
                "date": m.get("date", ""),
                "dateTimeGMT": m.get("dateTimeGMT", ""),
                "venue": m.get("venue", ""),
                "status": m.get("status", ""),
                "teams": teams,
                "teamInfo": team_info,
                "matchStarted": m.get("matchStarted", False),
                "matchEnded": m.get("matchEnded", False),
                "fantasyEnabled": m.get("fantasyEnabled", False),
            })

    # Sort by date
    team_matches.sort(key=lambda x: x.get("dateTimeGMT", ""))

    return {
        "team": team_short_upper,
        "total_matches": len(team_matches),
        "matches": team_matches,
    }


@router.get(
    "/match/{cricapi_id}/full-data",
    summary="Get ALL available data for a match (17 APIs combined)"
)
async def get_match_full_data(
    cricapi_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Returns combined data from all available APIs for a single match:
    - match_info (toss, winner, teams)
    - scorecard (full batting/bowling/catching)
    - fantasy_points (player points)
    - squad (playing XI)
    - ball_by_ball (extras/events)
    All data is fetched from MongoDB cache first, API only if cache miss.
    """
    import asyncio

    # Fetch all in parallel
    info_task = cached_cricket.get_match_info(db, cricapi_id)
    scorecard_task = cached_cricket.get_scorecard(db, cricapi_id)
    points_task = cached_cricket.get_match_points(db, cricapi_id)
    squad_task = cached_cricket.get_squad(db, cricapi_id)
    bbb_task = cached_cricket.get_match_bbb(db, cricapi_id)

    info, scorecard, points, squad, bbb = await asyncio.gather(
        info_task, scorecard_task, points_task, squad_task, bbb_task,
        return_exceptions=True
    )

    # Handle exceptions gracefully
    if isinstance(info, Exception):
        logger.error(f"match_info error: {info}")
        info = None
    if isinstance(scorecard, Exception):
        logger.error(f"scorecard error: {scorecard}")
        scorecard = None
    if isinstance(points, Exception):
        logger.error(f"match_points error: {points}")
        points = None
    if isinstance(squad, Exception):
        logger.error(f"squad error: {squad}")
        squad = None
    if isinstance(bbb, Exception):
        logger.error(f"bbb error: {bbb}")
        bbb = None

    # Parse scorecard metrics
    metrics = None
    if scorecard:
        from services.settlement_engine import parse_scorecard_to_metrics
        metrics = parse_scorecard_to_metrics(scorecard)

    # Build response
    result = {
        "cricapi_id": cricapi_id,
        "match_info": None,
        "scorecard": None,
        "fantasy_points": None,
        "squad": None,
        "ball_by_ball": None,
        "metrics": metrics,
        "available_sections": [],
    }

    if info:
        result["match_info"] = {
            "name": info.get("name", ""),
            "venue": info.get("venue", ""),
            "date": info.get("date", ""),
            "dateTimeGMT": info.get("dateTimeGMT", ""),
            "status": info.get("status", ""),
            "teams": info.get("teams", []),
            "teamInfo": info.get("teamInfo", []),
            "score": info.get("score", []),
            "tossWinner": info.get("tossWinner", ""),
            "tossChoice": info.get("tossChoice", ""),
            "matchWinner": info.get("matchWinner", ""),
            "matchStarted": info.get("matchStarted", False),
            "matchEnded": info.get("matchEnded", False),
        }
        result["available_sections"].append("match_info")

    if scorecard:
        result["scorecard"] = {
            "innings": scorecard.get("scorecard", []),
            "score_summary": scorecard.get("score", []),
            "teams": scorecard.get("teams", []),
            "teamInfo": scorecard.get("teamInfo", []),
        }
        result["available_sections"].append("scorecard")

    if points:
        result["fantasy_points"] = {
            "innings": points.get("innings", []),
            "totals": points.get("totals", []),
        }
        result["available_sections"].append("fantasy_points")

    if squad:
        result["squad"] = squad if isinstance(squad, list) else [squad]
        result["available_sections"].append("squad")

    if bbb:
        balls = bbb.get("bbb", []) if isinstance(bbb, dict) else []
        result["ball_by_ball"] = {
            "balls": balls,
            "total_events": len(balls),
        }
        result["available_sections"].append("ball_by_ball")

    return result


@router.get(
    "/cache-stats",
    summary="API cache statistics"
)
async def get_cache_stats(db: AsyncIOMotorDatabase = Depends(get_db)):
    """Shows how many API responses are cached in MongoDB."""
    stats = await cached_cricket.get_cache_stats(db)
    api_info = cricket_service.cricketdata.get_api_info()
    return {
        **stats,
        "api_hits_today": api_info.get("hits_today", 0),
        "api_hits_limit": api_info.get("hits_limit", 0),
        "api_hits_remaining": api_info.get("remaining", 0),
    }


# ==================== HELPER ====================

def _get_team_aliases(short: str) -> list:
    """Get all possible name variations for a team."""
    aliases = {
        "MI": ["MI", "Mumbai Indians"],
        "CSK": ["CSK", "Chennai Super Kings"],
        "RCB": ["RCB", "RCBW", "Royal Challengers Bangalore", "Royal Challengers Bengaluru"],
        "RCBW": ["RCB", "RCBW", "Royal Challengers Bangalore", "Royal Challengers Bengaluru"],
        "KKR": ["KKR", "Kolkata Knight Riders"],
        "DC": ["DC", "Delhi Capitals"],
        "PBKS": ["PBKS", "PK", "Punjab Kings"],
        "PK": ["PBKS", "PK", "Punjab Kings"],
        "SRH": ["SRH", "SH", "Sunrisers Hyderabad"],
        "SH": ["SRH", "SH", "Sunrisers Hyderabad"],
        "RR": ["RR", "Rajasthan Royals"],
        "GT": ["GT", "Gujarat Titans"],
        "LSG": ["LSG", "Lucknow Super Giants"],
    }
    return aliases.get(short, [short])
