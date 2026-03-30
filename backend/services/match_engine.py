"""
Bharat 11 — Match Engine Service
Handles:
1. Answer deadline enforcement (Stage 2)
2. Default template fallback (Stage 3)
3. Contest auto-live 24h before match (Stage 4)
"""
import logging
from datetime import datetime, timezone, timedelta
from models.schemas import generate_id, utc_now

logger = logging.getLogger(__name__)


# ==================== DEADLINE RULES ====================
# Hard rules from user:
# Full match → answer up to 1st innings 12th over, editable before
# In-match 1st inn 1-12 → deadline: 1st innings 5th over
# In-match 1st inn 12.1-20 → deadline: 1st innings 14.6 over
# In-match 2nd inn 1-12 → deadline: 2nd innings 5th over
# In-match 2nd inn 12.1-20 → deadline: 2nd innings 14.6 over

def get_deadline_for_template(template: dict) -> dict:
    """
    Returns the deadline specification for a template.
    Returns: {"innings": int, "over": float} — the latest over at which user can submit.
    """
    t_type = template.get("template_type", "full_match")

    if t_type == "full_match":
        return {"innings": 1, "over": 12.0}

    # In-match: use over_start/over_end and innings_range
    innings_range = template.get("innings_range", [])
    over_start = template.get("over_start", 1)
    over_end = template.get("over_end", 20)

    target_innings = innings_range[0] if innings_range else 1

    # 1-12 overs → deadline at 5th over of that innings
    # 12.1-20 overs → deadline at 14.6 over of that innings
    if over_start <= 12 and over_end <= 12:
        return {"innings": target_innings, "over": 5.0}
    elif over_start > 12:
        return {"innings": target_innings, "over": 14.6}
    else:
        # Covers full innings (1-20) → same as 1-12 rule
        return {"innings": target_innings, "over": 5.0}


def check_deadline_passed(template: dict, current_innings: int, current_over: float) -> bool:
    """
    Check if the answer deadline has passed for a template.
    Returns True if LOCKED (deadline passed), False if OPEN.
    """
    deadline = get_deadline_for_template(template)
    deadline_innings = deadline["innings"]
    deadline_over = deadline["over"]

    # If match hasn't started (innings 0), all templates are open
    if current_innings <= 0:
        return False

    # If we're past the deadline innings entirely
    if current_innings > deadline_innings:
        return True

    # If we're in the deadline innings, check the over
    if current_innings == deadline_innings:
        if current_over > deadline_over:
            return True

    return False


async def get_match_current_state(match_id: str, db) -> dict:
    """
    Get current innings and over for a match.
    First tries live_score from DB, then fetches from API.
    Returns: {"innings": int, "over": float, "status": str}
    """
    match = await db.matches.find_one({"id": match_id}, {"_id": 0, "live_score": 1, "status": 1})
    if not match:
        return {"innings": 0, "over": 0.0, "status": "unknown"}

    status = match.get("status", "upcoming")
    if status == "upcoming":
        return {"innings": 0, "over": 0.0, "status": "upcoming"}

    live_score = match.get("live_score", {})
    scores = live_score.get("scores", [])

    if not scores:
        return {"innings": 0, "over": 0.0, "status": status}

    current_innings = len(scores)
    last_score = scores[-1] if scores else {}
    current_over = float(last_score.get("overs", 0))

    return {"innings": current_innings, "over": current_over, "status": status}


async def check_can_submit(template: dict, match_id: str, db) -> dict:
    """
    Full check: can a user submit answers for this template right now?
    Returns: {"can_submit": bool, "reason": str, "deadline": dict, "current": dict}
    """
    state = await get_match_current_state(match_id, db)

    # If match is upcoming (not started), all templates are open
    if state["status"] == "upcoming":
        return {
            "can_submit": True,
            "reason": "Match hasn't started yet — all templates open",
            "deadline": get_deadline_for_template(template),
            "current": state
        }

    # If match is completed, nothing is open
    if state["status"] == "completed":
        return {
            "can_submit": False,
            "reason": "Match is completed — all templates locked",
            "deadline": get_deadline_for_template(template),
            "current": state
        }

    # Match is live — check deadlines
    locked = check_deadline_passed(template, state["innings"], state["over"])
    deadline = get_deadline_for_template(template)

    if locked:
        return {
            "can_submit": False,
            "reason": f"Deadline passed! Innings {deadline['innings']}, Over {deadline['over']}",
            "deadline": deadline,
            "current": state
        }

    return {
        "can_submit": True,
        "reason": f"Open until Innings {deadline['innings']}, Over {deadline['over']}",
        "deadline": deadline,
        "current": state
    }


# ==================== DEFAULT TEMPLATE FALLBACK (Stage 3) ====================

async def apply_default_template_fallback(match_id: str, db):
    """
    If a match has no templates, copy templates from the most recent completed match.
    """
    match = await db.matches.find_one({"id": match_id}, {"_id": 0})
    if not match:
        return {"applied": False, "reason": "Match not found"}

    existing = match.get("templates_assigned", [])
    if existing and len(existing) > 0:
        return {"applied": False, "reason": f"Match already has {len(existing)} templates"}

    # Find the most recent match with templates (by start_time descending)
    last_match = await db.matches.find_one(
        {
            "id": {"$ne": match_id},
            "templates_assigned": {"$exists": True, "$ne": []},
        },
        {"_id": 0, "id": 1, "templates_assigned": 1},
        sort=[("start_time", -1)]
    )

    if not last_match or not last_match.get("templates_assigned"):
        return {"applied": False, "reason": "No previous match with templates found"}

    # Copy templates: duplicate them with new IDs
    source_template_ids = last_match["templates_assigned"]
    source_templates = await db.templates.find(
        {"id": {"$in": source_template_ids}},
        {"_id": 0}
    ).to_list(length=10)

    if not source_templates:
        return {"applied": False, "reason": "Source templates not found"}

    now = utc_now().isoformat()
    new_template_ids = []
    team_a = match.get("team_a", {}).get("short_name", "TM1")
    team_b = match.get("team_b", {}).get("short_name", "TM2")

    for t in source_templates:
        new_id = generate_id()
        new_t = {**t}
        new_t["id"] = new_id
        new_t["name"] = f"{team_a} vs {team_b} — {t.get('phase_label', t.get('template_type', 'Match'))}"
        new_t["created_at"] = now
        new_t["updated_at"] = now
        new_t.pop("_id", None)
        await db.templates.insert_one(new_t)
        new_template_ids.append(new_id)

    # Assign to match
    await db.matches.update_one(
        {"id": match_id},
        {"$set": {"templates_assigned": new_template_ids, "updated_at": now}}
    )

    return {
        "applied": True,
        "templates_copied": len(new_template_ids),
        "from_match": last_match["id"],
        "template_ids": new_template_ids
    }


# ==================== CONTEST AUTO-LIVE 24H (Stage 4) ====================

async def auto_create_contests_24h(db):
    """
    Auto-create contests for matches starting within 24 hours.
    Runs as a background task every 30 minutes.
    """
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(hours=24)

    # Find upcoming matches starting within 24h that don't have open contests
    upcoming = await db.matches.find(
        {
            "status": "upcoming",
            "start_time": {"$lte": cutoff.isoformat(), "$gte": now.isoformat()}
        },
        {"_id": 0}
    ).to_list(length=20)

    results = []
    for match in upcoming:
        match_id = match["id"]
        team_a = match.get("team_a", {}).get("short_name", "TM1")
        team_b = match.get("team_b", {}).get("short_name", "TM2")

        # Check if contest already exists
        existing = await db.contests.find_one(
            {"match_id": match_id, "status": {"$in": ["open", "live"]}},
            {"_id": 0, "id": 1}
        )
        if existing:
            results.append({"match_id": match_id, "status": "skipped", "reason": "Contest already exists"})
            continue

        # Apply default template fallback if no templates
        templates = match.get("templates_assigned", [])
        if not templates:
            fallback = await apply_default_template_fallback(match_id, db)
            if fallback["applied"]:
                templates = fallback.get("template_ids", [])
                logger.info(f"Default templates applied to {team_a} vs {team_b}: {len(templates)}")

        # Get template with most questions for the contest
        full_template = None
        if templates:
            full_template = await db.templates.find_one(
                {"id": {"$in": templates}, "template_type": "full_match"},
                {"_id": 0, "id": 1, "question_ids": 1}
            )
            if not full_template:
                full_template = await db.templates.find_one(
                    {"id": {"$in": templates}},
                    {"_id": 0, "id": 1, "question_ids": 1}
                )

        template_id = full_template["id"] if full_template else None

        # Create contest
        contest = {
            "id": generate_id(),
            "name": f"{team_a} vs {team_b} Mega Contest",
            "match_id": match_id,
            "template_id": template_id,
            "templates_assigned": templates,
            "entry_fee": 1000,
            "prize_pool": 0,
            "max_participants": 100,
            "current_participants": 0,
            "prize_distribution": {"1st": 50, "2nd": 30, "3rd": 20},
            "status": "open",
            "auto_created": True,
            "created_at": utc_now().isoformat(),
            "updated_at": utc_now().isoformat(),
        }
        await db.contests.insert_one(contest)
        results.append({
            "match_id": match_id,
            "contest_id": contest["id"],
            "status": "created",
            "name": contest["name"],
            "templates": len(templates)
        })
        logger.info(f"Auto-contest created: {contest['name']} (ID: {contest['id']})")

        # Emit Socket.IO event for new contest
        try:
            from services.socket_manager import emit_contest_created
            await emit_contest_created(contest)
        except Exception as e:
            logger.debug(f"Socket emit (contest_created) failed: {e}")

        # Push notification: new contest live
        try:
            from services.push_manager import notify_contest_live
            await notify_contest_live(db, contest["name"], match_id)
        except Exception as e:
            logger.debug(f"Push notify (contest_live) failed: {e}")

    return {"processed": len(upcoming), "results": results}
