"""
IPL Search & Data Router
Comprehensive search across players, teams, matches, records.
"""
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from core.database import get_db
import re

router = APIRouter(prefix="/ipl", tags=["IPL Data"])


@router.get("/search")
async def ipl_search(
    q: str = Query(..., min_length=1, max_length=100),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    World's most comprehensive IPL search.
    Searches across: players, teams, matches, records.
    """
    pattern = re.compile(re.escape(q), re.IGNORECASE)
    results = {"players": [], "teams": [], "matches": [], "records": []}

    # Search Players
    player_cursor = db.ipl_players.find(
        {"$or": [
            {"name": pattern},
            {"name_hi": pattern},
            {"current_team": pattern},
            {"role": pattern},
            {"nationality": pattern},
        ]},
        {"_id": 0}
    ).limit(15)
    results["players"] = await player_cursor.to_list(length=15)

    # Search Matches
    match_cursor = db.matches.find(
        {"$or": [
            {"team_a.short_name": pattern},
            {"team_b.short_name": pattern},
            {"team_a.name": pattern},
            {"team_b.name": pattern},
            {"venue": pattern},
        ]},
        {"_id": 0, "id": 1, "team_a": 1, "team_b": 1, "venue": 1, "status": 1, "start_time": 1, "live_score": 1}
    ).limit(10)
    results["matches"] = await match_cursor.to_list(length=10)

    # Search Records
    record_cursor = db.ipl_records.find(
        {"$or": [
            {"title": pattern},
            {"holder": pattern},
            {"team": pattern},
        ]},
        {"_id": 0}
    ).limit(10)
    results["records"] = await record_cursor.to_list(length=10)

    # Team info search (static)
    team_names = {
        "MI": "Mumbai Indians", "CSK": "Chennai Super Kings", "RCB": "Royal Challengers Bengaluru",
        "KKR": "Kolkata Knight Riders", "DC": "Delhi Capitals", "PBKS": "Punjab Kings",
        "SRH": "Sunrisers Hyderabad", "RR": "Rajasthan Royals", "GT": "Gujarat Titans", "LSG": "Lucknow Super Giants"
    }
    for short, name in team_names.items():
        if q.lower() in short.lower() or q.lower() in name.lower():
            results["teams"].append({"short": short, "name": name})

    total = sum(len(v) for v in results.values())
    return {"query": q, "total": total, "results": results}


@router.get("/records")
async def get_ipl_records(
    db: AsyncIOMotorDatabase = Depends(get_db),
    category: str = Query(default=None)
):
    """Get all IPL records, optionally filtered by category. Redis cached 10min."""
    from services.redis_cache import cache_get, cache_set, CacheTTL
    cache_key = f"ipl:records:c={category or 'all'}"
    cached = await cache_get(cache_key)
    if cached:
        return cached
    query = {}
    if category:
        query["category"] = category
    cursor = db.ipl_records.find(query, {"_id": 0}).sort("category", 1)
    records = await cursor.to_list(length=200)
    result = {"records": records, "total": len(records)}
    await cache_set(cache_key, result, CacheTTL.IPL_RECORDS)
    return result


@router.get("/players")
async def get_ipl_players(
    db: AsyncIOMotorDatabase = Depends(get_db),
    role: str = Query(default=None),
    team: str = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100)
):
    """Get IPL player profiles. Redis cached 10min."""
    from services.redis_cache import cache_get, cache_set, CacheTTL
    cache_key = f"ipl:players:r={role or ''}:t={team or ''}:l={limit}"
    cached = await cache_get(cache_key)
    if cached:
        return cached
    query = {}
    if role:
        query["role"] = re.compile(re.escape(role), re.IGNORECASE)
    if team:
        query["$or"] = [
            {"current_team": re.compile(re.escape(team), re.IGNORECASE)},
            {"teams_history": re.compile(re.escape(team), re.IGNORECASE)}
        ]
    cursor = db.ipl_players.find(query, {"_id": 0}).limit(limit)
    players = await cursor.to_list(length=limit)
    result = {"players": players, "total": len(players)}
    await cache_set(cache_key, result, CacheTTL.IPL_PLAYERS)
    return result


@router.get("/players/{player_name}")
async def get_player_profile(
    player_name: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get detailed player profile by name."""
    player = await db.ipl_players.find_one(
        {"name": re.compile(re.escape(player_name), re.IGNORECASE)},
        {"_id": 0}
    )
    if not player:
        return {"error": "Player not found", "player": None}
    return {"player": player}


@router.get("/caps")
async def get_cap_winners(
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get Orange Cap and Purple Cap winners history. Redis cached 10min."""
    from services.redis_cache import cache_get, cache_set, CacheTTL
    cached = await cache_get("ipl:caps")
    if cached:
        return cached
    cursor = db.ipl_caps.find({}, {"_id": 0}).sort("year", -1)
    caps = await cursor.to_list(length=20)
    result = {"cap_winners": caps, "total": len(caps)}
    await cache_set("ipl:caps", result, CacheTTL.IPL_CAPS)
    return result


@router.get("/seed")
async def seed_ipl_data_endpoint(
    db: AsyncIOMotorDatabase = Depends(get_db),
    force: bool = Query(default=False)
):
    """Seed IPL data into the database. Use force=true to replace all existing data."""
    from services.ipl_data_seeder import seed_ipl_data
    result = await seed_ipl_data(db, force=force)
    return {"message": "IPL data seeded", **result}


@router.get("/head-to-head")
async def head_to_head(
    player1: str = Query(..., min_length=1),
    player2: str = Query(..., min_length=1),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Compare two players head-to-head."""
    p1 = await db.ipl_players.find_one(
        {"name": re.compile(re.escape(player1), re.IGNORECASE)},
        {"_id": 0}
    )
    p2 = await db.ipl_players.find_one(
        {"name": re.compile(re.escape(player2), re.IGNORECASE)},
        {"_id": 0}
    )
    if not p1 or not p2:
        missing = []
        if not p1:
            missing.append(player1)
        if not p2:
            missing.append(player2)
        return {"error": f"Player(s) not found: {', '.join(missing)}", "players": []}

    return {"player1": p1, "player2": p2}
