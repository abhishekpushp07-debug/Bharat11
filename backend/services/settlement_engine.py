"""
Bharat 11 - Auto-Settlement Engine (Layer 3 & 4)
The BRAIN of the Auto Pipeline.

Uses CricketData.org Premium Scorecard API to:
1. Fetch detailed scorecard (batting/bowling/extras per innings)
2. Parse into flat metrics dict (innings_1_total_runs, match_total_sixes, etc.)
3. Evaluate unresolved questions against metrics
4. Auto-resolve questions when conditions are met
5. Auto-finalize contests when all questions resolved

Metrics extracted from scorecard:
- Match level: total_runs, total_wickets, total_sixes, total_fours, winner, toss
- Per innings: runs, wickets, overs, run_rate, sixes, fours, extras, highest_score
- Top performers: highest_run_scorer, best_bowler

Question auto_resolution config:
{
  "metric": "innings_1_total_runs",
  "trigger": "innings_1_end" | "match_end",
  "resolution_type": "range" | "text_match" | "boolean"
}
"""
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


# ==================== SCORECARD PARSER ====================

def parse_scorecard_to_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert CricketData.org scorecard response to flat metrics dict.
    Input: data field from match_scorecard API response.
    Output: flat dict like {innings_1_total_runs: 175, match_total_sixes: 14, ...}
    """
    metrics = {
        "match_completed": False,
        "match_winner": "",
        "toss_winner": "",
        "toss_choice": "",
        "match_status": "",
        "match_total_runs": 0,
        "match_total_wickets": 0,
        "match_total_sixes": 0,
        "match_total_fours": 0,
        "match_total_extras": 0,
        "innings_count": 0,
        "highest_run_scorer": "",
        "highest_run_scorer_runs": 0,
        "best_bowler": "",
        "best_bowler_wickets": 0,
    }

    if not data:
        return metrics

    # Match level
    status_text = data.get("status", "")
    metrics["match_status"] = status_text
    metrics["match_completed"] = any(
        w in status_text.lower()
        for w in ["won", "drawn", "tied", "no result", "abandoned"]
    )
    metrics["match_winner"] = data.get("matchWinner", "")
    metrics["toss_winner"] = data.get("tossWinner", "")
    metrics["toss_choice"] = data.get("tossChoice", "")

    # Parse score summaries
    scores = data.get("score", [])
    for s in scores:
        metrics["match_total_runs"] += s.get("r", 0)
        metrics["match_total_wickets"] += s.get("w", 0)

    # Parse detailed scorecard per innings
    scorecard = data.get("scorecard", [])
    metrics["innings_count"] = len(scorecard)

    top_scorer_runs = 0
    top_scorer_name = ""
    top_bowler_wickets = 0
    top_bowler_name = ""

    for idx, innings in enumerate(scorecard):
        inn_num = idx + 1
        prefix = f"innings_{inn_num}"

        # Totals — try from totals field first, fallback to score summary
        totals = innings.get("totals", {})
        score_summary = scores[idx] if idx < len(scores) else {}

        # Calculate from batting if totals are empty
        batting = innings.get("batting", [])
        calc_runs = sum(b.get("r", 0) for b in batting)
        calc_sixes = sum(b.get("6s", 0) for b in batting)
        calc_fours = sum(b.get("4s", 0) for b in batting)

        extras_obj = innings.get("extras", {})
        extras_runs = extras_obj.get("r", 0) if extras_obj else 0

        # Use totals.R if available, else score.r, else calculate from batting+extras
        inn_runs = totals.get("R") or score_summary.get("r", 0) or (calc_runs + extras_runs)
        inn_overs = totals.get("O") or score_summary.get("o", 0) or 0
        inn_wickets = totals.get("W") or score_summary.get("w", 0) or 0
        inn_rr = totals.get("RR", 0)
        if not inn_rr and inn_overs and inn_overs > 0:
            inn_rr = round(inn_runs / inn_overs, 2)

        metrics[f"{prefix}_total_runs"] = inn_runs
        metrics[f"{prefix}_total_overs"] = inn_overs
        metrics[f"{prefix}_total_wickets"] = inn_wickets
        metrics[f"{prefix}_run_rate"] = inn_rr
        metrics[f"{prefix}_completed"] = True  # If in scorecard, innings happened
        metrics[f"{prefix}_team"] = innings.get("inning", "").replace(f" Inning {inn_num}", "").strip()

        # Extras
        metrics[f"{prefix}_extras"] = extras_runs
        metrics[f"{prefix}_wides"] = extras_obj.get("w", 0) if extras_obj else 0
        metrics[f"{prefix}_no_balls"] = extras_obj.get("nb", 0) if extras_obj else 0
        metrics["match_total_extras"] += extras_runs

        # Batting stats (batting already read above)
        inn_sixes = calc_sixes
        inn_fours = calc_fours
        inn_highest = 0
        inn_highest_name = ""
        inn_ducks = 0
        inn_fifties = 0
        inn_centuries = 0

        for b in batting:
            runs = b.get("r", 0)
            name = b.get("batsman", {}).get("name", "")

            if runs > inn_highest:
                inn_highest = runs
                inn_highest_name = name

            if runs == 0 and b.get("dismissal"):
                inn_ducks += 1
            if 50 <= runs < 100:
                inn_fifties += 1
            if runs >= 100:
                inn_centuries += 1

            # Track overall top scorer
            if runs > top_scorer_runs:
                top_scorer_runs = runs
                top_scorer_name = name

        metrics[f"{prefix}_total_sixes"] = inn_sixes
        metrics[f"{prefix}_total_fours"] = inn_fours
        metrics[f"{prefix}_highest_score"] = inn_highest
        metrics[f"{prefix}_highest_scorer"] = inn_highest_name
        metrics[f"{prefix}_ducks"] = inn_ducks
        metrics[f"{prefix}_fifties"] = inn_fifties
        metrics[f"{prefix}_centuries"] = inn_centuries
        metrics["match_total_sixes"] += inn_sixes
        metrics["match_total_fours"] += inn_fours

        # Bowling stats
        bowling = innings.get("bowling", [])
        inn_maiden_overs = 0
        inn_best_bowler = ""
        inn_best_bowler_wickets = 0

        for bw in bowling:
            w = bw.get("w", 0)
            m = bw.get("m", 0)
            bw_name = bw.get("bowler", {}).get("name", "")
            inn_maiden_overs += m

            if w > inn_best_bowler_wickets:
                inn_best_bowler_wickets = w
                inn_best_bowler = bw_name

            if w > top_bowler_wickets:
                top_bowler_wickets = w
                top_bowler_name = bw_name

        metrics[f"{prefix}_maiden_overs"] = inn_maiden_overs
        metrics[f"{prefix}_best_bowler"] = inn_best_bowler
        metrics[f"{prefix}_best_bowler_wickets"] = inn_best_bowler_wickets

        # Catching stats
        catching = innings.get("catching", [])
        inn_catches = sum(c.get("catch", 0) for c in catching)
        inn_runouts = sum(c.get("runout", 0) for c in catching)
        inn_stumpings = sum(c.get("stumped", 0) for c in catching)
        metrics[f"{prefix}_catches"] = inn_catches
        metrics[f"{prefix}_runouts"] = inn_runouts
        metrics[f"{prefix}_stumpings"] = inn_stumpings

    metrics["highest_run_scorer"] = top_scorer_name
    metrics["highest_run_scorer_runs"] = top_scorer_runs
    metrics["best_bowler"] = top_bowler_name
    metrics["best_bowler_wickets"] = top_bowler_wickets

    return metrics


# ==================== TRIGGER CHECK ====================

def is_trigger_met(trigger: str, metrics: Dict[str, Any]) -> bool:
    """Check if the resolution trigger condition is met."""
    t = trigger.lower().strip()

    if t == "match_end":
        return metrics.get("match_completed", False)

    if t == "innings_1_end":
        return metrics.get("innings_count", 0) >= 1 and metrics.get("innings_1_completed", False)

    if t == "innings_2_end":
        return metrics.get("innings_count", 0) >= 2 and metrics.get("innings_2_completed", False)

    if t == "toss":
        return bool(metrics.get("toss_winner", ""))

    if t == "always":
        return True

    # Default: check if match completed
    return metrics.get("match_completed", False)


# ==================== QUESTION EVALUATOR ====================

def evaluate_question(question: Dict, metrics: Dict[str, Any]) -> Optional[str]:
    """
    Evaluate a question against scorecard metrics.
    Returns correct option key (A/B/C/D) or None if can't determine.

    Uses question's auto_resolution config:
    - metric: which metric to check
    - trigger: when to check
    - resolution_type: "range" (option min/max) | "text_match" (option text) | "boolean" (yes/no)
    """
    auto_res = question.get("auto_resolution")
    if not auto_res:
        return None

    metric_key = auto_res.get("metric", "")
    trigger = auto_res.get("trigger", "match_end")
    res_type = auto_res.get("resolution_type", "range")

    # Check trigger
    if not is_trigger_met(trigger, metrics):
        return None

    # Get metric value
    metric_value = metrics.get(metric_key)
    if metric_value is None:
        logger.debug(f"Metric '{metric_key}' not found in scorecard")
        return None

    options = question.get("options", [])
    if not options:
        return None

    # RANGE resolution: find option whose min/max contains the value
    if res_type == "range":
        numeric_val = float(metric_value) if metric_value != "" else 0
        for opt in options:
            min_v = opt.get("min_value")
            max_v = opt.get("max_value")
            if min_v is not None and max_v is not None:
                if float(min_v) <= numeric_val <= float(max_v):
                    return opt["key"]
            elif min_v is not None and max_v is None:
                # Open-ended upper (e.g., "200+")
                if numeric_val >= float(min_v):
                    return opt["key"]
            elif min_v is None and max_v is not None:
                # Open-ended lower (e.g., "Below 100")
                if numeric_val <= float(max_v):
                    return opt["key"]
        logger.debug(f"No range match for metric={metric_key}, value={numeric_val}")
        return None

    # TEXT_MATCH resolution: match metric text against option texts
    if res_type == "text_match":
        metric_str = str(metric_value).strip().lower()
        if not metric_str:
            return None
        for opt in options:
            opt_text = (opt.get("text_en", "") or "").strip().lower()
            opt_hi = (opt.get("text_hi", "") or "").strip().lower()
            # Check if metric contains the option text or vice versa
            if (metric_str in opt_text or opt_text in metric_str
                    or metric_str in opt_hi or opt_hi in metric_str):
                return opt["key"]
        logger.debug(f"No text match for metric={metric_key}, value={metric_str}")
        return None

    # BOOLEAN resolution: yes/no based on threshold
    if res_type == "boolean":
        threshold = auto_res.get("threshold", 0)
        comparator = auto_res.get("comparator", ">=")
        numeric_val = float(metric_value) if isinstance(metric_value, (int, float)) else 0
        result = False
        if comparator == ">=":
            result = numeric_val >= threshold
        elif comparator == ">":
            result = numeric_val > threshold
        elif comparator == "<=":
            result = numeric_val <= threshold
        elif comparator == "<":
            result = numeric_val < threshold
        elif comparator == "==":
            result = numeric_val == threshold

        # Option A = Yes, Option B = No (convention)
        return "A" if result else "B"

    return None


# ==================== AUTO-LINK CRICKETDATA ID ====================

async def _auto_link_cricketdata_id(match: Dict, db) -> Optional[str]:
    """
    Auto-link a CricketData.org match ID by matching team names.
    Fetches current matches from CricketData API and matches by team names.
    Stores the linked ID for future use.
    """
    import asyncio
    from services.cricket_data import cricket_service

    team_a_name = (match.get("team_a", {}).get("name", "") or "").lower()
    team_b_name = (match.get("team_b", {}).get("name", "") or "").lower()
    team_a_short = (match.get("team_a", {}).get("short_name", "") or "").lower()
    team_b_short = (match.get("team_b", {}).get("short_name", "") or "").lower()

    if not team_a_name and not team_a_short:
        return None

    # Fetch matches from CricketData API
    loop = asyncio.get_running_loop()
    api_matches = await loop.run_in_executor(None, cricket_service.cricketdata.fetch_matches)

    if not api_matches:
        return None

    for am in api_matches:
        am_ta = (am.get("team_a", {}).get("name", "") or "").lower()
        am_tb = (am.get("team_b", {}).get("name", "") or "").lower()
        am_ta_short = (am.get("team_a", {}).get("short_name", "") or "").lower()
        am_tb_short = (am.get("team_b", {}).get("short_name", "") or "").lower()

        # Match: team A and B names/shorts match in either order
        match_found = False

        # Direct match
        if ((team_a_short and team_a_short in (am_ta_short, am_ta)) and
            (team_b_short and team_b_short in (am_tb_short, am_tb))):
            match_found = True
        # Reversed match
        elif ((team_a_short and team_a_short in (am_tb_short, am_tb)) and
              (team_b_short and team_b_short in (am_ta_short, am_ta))):
            match_found = True
        # Full name match
        elif ((team_a_name in am_ta or am_ta in team_a_name) and
              (team_b_name in am_tb or am_tb in team_b_name)):
            match_found = True
        elif ((team_a_name in am_tb or am_tb in team_a_name) and
              (team_b_name in am_ta or am_ta in team_b_name)):
            match_found = True

        if match_found:
            cd_id = am.get("source_id", "")
            if cd_id:
                # Store for future use
                await db.matches.update_one(
                    {"id": match["id"]},
                    {"$set": {"cricketdata_id": cd_id}}
                )
                logger.info(f"Auto-linked CricketData ID {cd_id} to match {match['id']}")
                return cd_id

    return None


# ==================== SETTLEMENT RUNNER ====================

async def run_settlement_for_match(match_id: str, db) -> Dict[str, Any]:
    """
    Main settlement function for a match.
    1. Get match + find CricketData.org match ID (auto-link by team names if needed)
    2. Fetch scorecard from CricketData.org Premium API
    3. Parse metrics
    4. Evaluate all unresolved questions for all contests of this match
    5. Auto-resolve matched questions
    6. Auto-finalize contests if all questions resolved

    Returns settlement report.
    """
    from services.api_cache import cached_cricket

    match = await db.matches.find_one({"id": match_id}, {"_id": 0})
    if not match:
        return {"error": "Match not found", "resolved": 0}

    # Get CricketData.org match ID — check stored ID first, then auto-link
    cricketdata_id = match.get("cricketdata_id", "")

    if not cricketdata_id:
        # Try auto-linking by team names
        cricketdata_id = await _auto_link_cricketdata_id(match, db)

    if not cricketdata_id:
        return {
            "error": "Could not find CricketData.org match ID. Use 'Link Match' to connect manually.",
            "resolved": 0,
            "match_id": match_id
        }

    # Fetch scorecard (via cache)
    scorecard_data = await cached_cricket.get_scorecard(db, cricketdata_id)
    if not scorecard_data:
        return {"error": "Could not fetch scorecard from CricketData API", "resolved": 0}

    # Parse metrics
    metrics = parse_scorecard_to_metrics(scorecard_data)

    # Get all contests for this match
    contests_cursor = db.contests.find(
        {"match_id": match_id, "status": {"$ne": "completed"}},
        {"_id": 0}
    )
    contests = await contests_cursor.to_list(length=50)

    if not contests:
        return {
            "match_id": match_id,
            "metrics": metrics,
            "message": "No active contests for this match",
            "resolved": 0,
            "scorecard_fetched": True
        }

    total_resolved = 0
    total_already_resolved = 0
    total_skipped = 0
    contest_reports = []

    for contest in contests:
        contest_id = contest["id"]
        template_id = contest.get("template_id")

        # Get template questions
        template = await db.templates.find_one({"id": template_id}, {"_id": 0})
        if not template:
            continue

        qids = template.get("question_ids", [])
        if not qids:
            continue

        # Get questions
        q_cursor = db.questions.find({"id": {"$in": qids}}, {"_id": 0})
        questions = await q_cursor.to_list(length=len(qids))

        # Check which are already resolved
        resolved_cursor = db.question_results.find(
            {"match_id": match_id, "question_id": {"$in": qids}},
            {"_id": 0, "question_id": 1, "correct_option": 1}
        )
        resolved_list = await resolved_cursor.to_list(length=len(qids))
        resolved_set = {r["question_id"] for r in resolved_list}

        contest_resolved = 0
        contest_skipped = 0

        for q in questions:
            qid = q["id"]

            # Skip already resolved
            if qid in resolved_set:
                total_already_resolved += 1
                continue

            # Try auto-evaluation
            correct_option = evaluate_question(q, metrics)
            if correct_option is None:
                total_skipped += 1
                contest_skipped += 1
                continue

            # AUTO-RESOLVE: Use the same logic as manual resolve
            await _resolve_question_internal(db, contest_id, match_id, qid, correct_option, q)
            total_resolved += 1
            contest_resolved += 1
            resolved_set.add(qid)

        # Check if all questions resolved → auto-finalize
        all_resolved = len(resolved_set) >= len(qids)
        auto_finalized = False
        if all_resolved and contest.get("status") != "completed":
            finalize_result = await _auto_finalize_contest(db, contest_id)
            auto_finalized = finalize_result.get("finalized", False)

        contest_reports.append({
            "contest_id": contest_id,
            "contest_name": contest.get("name", ""),
            "total_questions": len(qids),
            "already_resolved": len(resolved_set) - contest_resolved,
            "auto_resolved": contest_resolved,
            "skipped": contest_skipped,
            "all_resolved": all_resolved,
            "auto_finalized": auto_finalized,
        })

    # Update match live_score with latest scorecard data
    score_summary = scorecard_data.get("score", [])
    live_score_data = {
        "scores": score_summary,
        "status_text": scorecard_data.get("status", ""),
        "toss_winner": scorecard_data.get("tossWinner", ""),
        "match_winner": scorecard_data.get("matchWinner", ""),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.matches.update_one(
        {"id": match_id},
        {"$set": {
            "live_score": live_score_data,
            "status": "completed" if metrics["match_completed"] else match.get("status", "live"),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    # Emit live score via Socket.IO
    try:
        from services.socket_manager import emit_live_score, emit_contest_finalized
        await emit_live_score(match_id, live_score_data)
        # Emit finalized contests
        for cr in contest_reports:
            if cr.get("auto_finalized"):
                await emit_contest_finalized(cr["contest_id"], match_id, [])
    except Exception as e:
        logger.debug(f"Socket emit (live_score) failed: {e}")

    return {
        "match_id": match_id,
        "scorecard_fetched": True,
        "match_completed": metrics["match_completed"],
        "match_winner": metrics.get("match_winner", ""),
        "total_resolved": total_resolved,
        "total_already_resolved": total_already_resolved,
        "total_skipped": total_skipped,
        "contests": contest_reports,
        "key_metrics": {
            "innings_1_runs": metrics.get("innings_1_total_runs", 0),
            "innings_2_runs": metrics.get("innings_2_total_runs", 0),
            "total_sixes": metrics.get("match_total_sixes", 0),
            "total_fours": metrics.get("match_total_fours", 0),
            "highest_scorer": f"{metrics.get('highest_run_scorer', '')} ({metrics.get('highest_run_scorer_runs', 0)})",
            "best_bowler": f"{metrics.get('best_bowler', '')} ({metrics.get('best_bowler_wickets', 0)}w)",
        }
    }


def get_streak_multiplier(streak: int) -> int:
    """Get points multiplier based on prediction streak. 5+=2x, 10+=4x."""
    if streak >= 10:
        return 4
    elif streak >= 5:
        return 2
    return 1


async def update_user_streaks(db, user_correct_map: Dict[str, bool], points_map: Dict[str, int] = None) -> Dict[str, Dict]:
    """
    Batch update prediction streaks for users after question resolution.
    user_correct_map: {user_id: True/False}
    Returns: {user_id: {"new_streak": int, "multiplier": int, "bonus": int}}
    """
    from pymongo import UpdateOne

    user_ids = list(user_correct_map.keys())
    if not user_ids:
        return {}

    # Batch read current streaks
    users_cursor = db.users.find(
        {"id": {"$in": user_ids}},
        {"_id": 0, "id": 1, "prediction_streak": 1, "max_prediction_streak": 1}
    )
    users_data = await users_cursor.to_list(length=len(user_ids))
    streak_data = {u["id"]: (u.get("prediction_streak", 0), u.get("max_prediction_streak", 0)) for u in users_data}

    streak_ops = []
    results = {}

    for user_id, is_correct in user_correct_map.items():
        current_streak, max_streak = streak_data.get(user_id, (0, 0))

        if is_correct:
            new_streak = current_streak + 1
            multiplier = get_streak_multiplier(new_streak)
            base_points = (points_map or {}).get(user_id, 0)
            bonus = base_points * (multiplier - 1)  # extra points on top of base

            update_set = {"prediction_streak": new_streak}
            if new_streak > max_streak:
                update_set["max_prediction_streak"] = new_streak

            streak_ops.append(UpdateOne({"id": user_id}, {"$set": update_set}))
            results[user_id] = {"new_streak": new_streak, "multiplier": multiplier, "bonus": bonus}
        else:
            streak_ops.append(UpdateOne({"id": user_id}, {"$set": {"prediction_streak": 0}}))
            results[user_id] = {"new_streak": 0, "multiplier": 1, "bonus": 0}

    if streak_ops:
        await db.users.bulk_write(streak_ops)

    return results


async def _resolve_question_internal(db, contest_id: str, match_id: str, question_id: str, correct_option: str, question: Dict):
    """Internal question resolution with streak tracking and multiplier bonuses."""
    from pymongo import UpdateOne
    from models.schemas import generate_id, utc_now

    now = utc_now().isoformat()
    points_value = question.get("points", 10)

    # Store question result
    await db.question_results.insert_one({
        "id": generate_id(),
        "match_id": match_id,
        "question_id": question_id,
        "correct_option": correct_option,
        "auto_resolved": True,
        "resolved_at": now,
        "created_at": now,
        "updated_at": now
    })

    # Update question's correct_option
    await db.questions.update_one(
        {"id": question_id},
        {"$set": {"correct_option": correct_option}}
    )

    # Batch score all entries
    entries_cursor = db.contest_entries.find(
        {"contest_id": contest_id, "predictions.question_id": question_id}
    )
    entries = await entries_cursor.to_list(length=10000)

    # Phase 1: Score with base points
    bulk_ops = []
    user_correct_map = {}
    user_points_map = {}

    for entry in entries:
        for i, pred in enumerate(entry.get("predictions", [])):
            if pred["question_id"] == question_id:
                is_correct = pred["selected_option"] == correct_option
                earned = points_value if is_correct else 0
                user_correct_map[entry["user_id"]] = is_correct
                if is_correct:
                    user_points_map[entry["user_id"]] = points_value
                bulk_ops.append(UpdateOne(
                    {"_id": entry["_id"], f"predictions.{i}.question_id": question_id},
                    {"$set": {
                        f"predictions.{i}.is_correct": is_correct,
                        f"predictions.{i}.points_earned": earned
                    },
                    "$inc": {"total_points": earned}}
                ))
                break

    if bulk_ops:
        await db.contest_entries.bulk_write(bulk_ops)

    # Phase 2: Update streaks and apply bonus multiplier
    streak_results = await update_user_streaks(db, user_correct_map, user_points_map)

    # Phase 3: Apply streak bonus points to entries
    bonus_ops = []
    for entry in entries:
        uid = entry["user_id"]
        sr = streak_results.get(uid)
        if sr and sr["bonus"] > 0:
            for i, pred in enumerate(entry.get("predictions", [])):
                if pred["question_id"] == question_id:
                    bonus_ops.append(UpdateOne(
                        {"_id": entry["_id"], f"predictions.{i}.question_id": question_id},
                        {
                            "$inc": {
                                f"predictions.{i}.points_earned": sr["bonus"],
                                "total_points": sr["bonus"]
                            },
                            "$set": {
                                f"predictions.{i}.streak_multiplier": sr["multiplier"]
                            }
                        }
                    ))
                    break

    if bonus_ops:
        await db.contest_entries.bulk_write(bonus_ops)

    streak_bonuses = sum(sr["bonus"] for sr in streak_results.values() if sr["bonus"] > 0)
    logger.info(f"Auto-resolved Q:{question_id} → {correct_option} | {len(entries)} entries scored | Streak bonuses: {streak_bonuses}")

    # Phase 4: Emit Socket.IO events
    try:
        from services.socket_manager import emit_question_resolved, emit_leaderboard_update
        await emit_question_resolved(contest_id, match_id, question_id, correct_option, len(entries))
        await emit_leaderboard_update(contest_id, match_id)
    except Exception as e:
        logger.debug(f"Socket emit failed (non-critical): {e}")


async def _auto_finalize_contest(db, contest_id: str) -> Dict:
    """Auto-finalize a contest: calculate ranks, distribute prizes."""
    from pymongo import UpdateOne
    from models.schemas import generate_id, utc_now

    contest = await db.contests.find_one({"id": contest_id})
    if not contest or contest.get("status") == "completed":
        return {"finalized": False}

    now = utc_now().isoformat()

    # Get entries sorted
    entries_cursor = db.contest_entries.find(
        {"contest_id": contest_id}
    ).sort([("total_points", -1), ("submission_time", 1)])
    entries = await entries_cursor.to_list(length=10000)

    if not entries:
        await db.contests.update_one(
            {"id": contest_id},
            {"$set": {"status": "completed", "auto_finalized": True, "updated_at": now}}
        )
        return {"finalized": True, "entries": 0, "prizes": 0}

    # Prize pool: entry_fee × participants (50/30/20)
    entry_fee = contest.get("entry_fee", 1000)
    total_pool = entry_fee * len(entries)
    prize_map = {
        1: int(total_pool * 0.50),
        2: int(total_pool * 0.30),
        3: int(total_pool * 0.20),
    }

    bulk_ops = []
    total_prizes = 0

    for rank, entry in enumerate(entries, 1):
        prize = prize_map.get(rank, 0)
        total_prizes += prize
        bulk_ops.append(UpdateOne(
            {"_id": entry["_id"]},
            {"$set": {"final_rank": rank, "prize_won": prize, "updated_at": now}}
        ))

        if prize > 0:
            user = await db.users.find_one({"id": entry["user_id"]})
            if user:
                new_balance = user["coins_balance"] + prize
                await db.users.update_one(
                    {"id": entry["user_id"]},
                    {"$inc": {"coins_balance": prize, "contests_won": 1}}
                )
                await db.wallet_transactions.insert_one({
                    "id": generate_id(),
                    "user_id": entry["user_id"],
                    "type": "credit",
                    "amount": prize,
                    "reason": "contest_win",
                    "reference_id": contest_id,
                    "balance_after": new_balance,
                    "description": f"[AUTO] Rank #{rank} - Prize: {prize} coins",
                    "created_at": now,
                    "updated_at": now
                })

    if bulk_ops:
        await db.contest_entries.bulk_write(bulk_ops)

    # Update participants' matches_played
    user_ids = [e["user_id"] for e in entries]
    if user_ids:
        await db.users.update_many(
            {"id": {"$in": user_ids}},
            {"$inc": {"matches_played": 1}}
        )

    # Mark contest completed
    await db.contests.update_one(
        {"id": contest_id},
        {"$set": {"status": "completed", "auto_finalized": True, "updated_at": now}}
    )

    logger.info(f"Auto-finalized contest {contest_id}: {len(entries)} entries, {total_prizes} coins distributed")
    return {"finalized": True, "entries": len(entries), "prizes": total_prizes}


# ==================== METRICS FETCH (for Admin UI) ====================

async def fetch_match_metrics(match_id: str, db) -> Dict[str, Any]:
    """Fetch scorecard and return parsed metrics + raw scores for display."""
    from services.api_cache import cached_cricket

    match = await db.matches.find_one({"id": match_id}, {"_id": 0})
    if not match:
        return {"error": "Match not found"}

    cd_id = match.get("cricketdata_id", "")
    if not cd_id:
        # Try auto-link
        cd_id = await _auto_link_cricketdata_id(match, db)
    if not cd_id:
        return {"error": "No CricketData ID linked"}

    scorecard_data = await cached_cricket.get_scorecard(db, cd_id)
    if not scorecard_data:
        return {"error": "Could not fetch scorecard"}

    metrics = parse_scorecard_to_metrics(scorecard_data)

    return {
        "match_id": match_id,
        "metrics": metrics,
        "raw_scores": scorecard_data.get("score", []),
        "raw_scorecard": scorecard_data.get("scorecard", []),
        "match_name": scorecard_data.get("name", ""),
        "venue": scorecard_data.get("venue", ""),
    }
