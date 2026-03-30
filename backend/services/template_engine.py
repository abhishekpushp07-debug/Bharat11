"""
Bharat 11 — 5-Template Auto-Engine
Auto-generates 5 templates per match from the 200-question pool.

Template Strategy:
1. Full Match — match_end + toss trigger questions (all categories)
2. Innings 1 Powerplay — innings_1_end trigger, PP-focused metrics (overs 1-6)
3. Innings 1 Death — innings_1_end trigger, death-focused metrics (overs 16-20)
4. Innings 2 Powerplay — match_end trigger, 2nd innings PP metrics (overs 1-6)
5. Innings 2 Death — match_end trigger, 2nd innings death metrics (overs 16-20)
"""
import random
from models.schemas import generate_id, utc_now


# Question routing rules — maps trigger+metric patterns to template slots
TEMPLATE_CONFIGS = [
    {
        "name": "Full Match Predictions",
        "template_type": "full_match",
        "phase_label": "Full Match",
        "innings_range": [1, 2],
        "over_start": None,
        "over_end": None,
        "answer_deadline_over": None,
        "description": "Predict match outcomes before it starts!",
        "trigger_filter": None,  # special handling: match_end + toss
        "metric_keywords": [
            "match_total", "match_winner", "toss", "victory",
            "batting_first_win", "chasing_win", "chase_success",
            "super_over", "rain_delay", "match_last_over",
            "innings_run_diff", "higher_scoring_innings",
            "match_total_overs", "match_pace", "match_highest_partnership",
            "innings_break", "both_teams_160", "match_fifties",
            "match_centuries", "match_total_ducks", "match_total_boundaries",
            "match_best_economy", "highest_run_scorer", "best_bowler_wickets",
            "match_total_wickets", "match_total_caught", "match_total_bowled",
            "match_total_lbw", "match_total_runouts", "match_total_stumpings",
            "match_total_extras", "match_total_wides", "match_total_noballs",
            "match_total_byes", "match_total_sixes", "match_total_fours",
            "match_total_dots", "match_hit_wicket", "match_total_cb",
            "match_penalty_runs", "match_retired_hurt", "match_single_digit",
            "more_sixes_innings", "more_runs_innings", "more_wickets_innings",
            "players_30plus", "bowlers_2plus", "match_highest_sr",
            "allrounder_40", "fastest_fifty", "max_sixes_by",
            "max_fours_by", "opener_top_scorer", "keeper_catches",
            "max_catches_by", "top_scorer_sr", "match_middle_runs",
            "match_death_sixes", "match_death_boundaries", "match_death_rr",
            "match_death_wides", "match_death_noballs", "match_death_dots",
            "match_death_runs", "match_pp_sixes", "match_pp_fours",
            "match_pp_runs", "match_pp_wickets", "better_pp_team",
            "higher_pp_innings", "match_opener_30_pp",
            "first_ball_outcome", "innings_2_first_ball",
            "innings_2_req_rr", "innings_2_rr_at_15",
            "combined_match_score",
        ],
        "max_questions": 15,
    },
    {
        "name": "Innings 1 Powerplay",
        "template_type": "in_match",
        "phase_label": "Innings 1 - Powerplay (Overs 1-6)",
        "innings_range": [1],
        "over_start": 1,
        "over_end": 6,
        "answer_deadline_over": 1,  # Must answer before over 1 of innings 1
        "description": "Predict the 1st innings powerplay!",
        "trigger_filter": "innings_1_end",
        "metric_keywords": [
            "innings_1_pp_runs", "innings_1_pp_wickets", "innings_1_pp_boundaries",
            "innings_1_pp_sixes", "innings_1_pp_fours", "innings_1_pp_rr",
            "innings_1_pp_wides", "innings_1_pp_extras", "innings_1_pp_dots",
            "innings_1_pp_noballs", "innings_1_first_over",
            "innings_1_first3_runs", "innings_1_first_wicket_over",
        ],
        "max_questions": 10,
    },
    {
        "name": "Innings 1 Death Overs",
        "template_type": "in_match",
        "phase_label": "Innings 1 - Death Overs (16-20)",
        "innings_range": [1],
        "over_start": 16,
        "over_end": 20,
        "answer_deadline_over": 15,  # Must answer before over 15 ends
        "description": "Predict the 1st innings death overs!",
        "trigger_filter": "innings_1_end",
        "metric_keywords": [
            "innings_1_death_runs", "innings_1_death_wickets",
            "innings_1_death_sixes", "innings_1_death_fours",
            "innings_1_death_extras",
            "innings_1_over18_runs", "innings_1_over19_runs",
            "innings_1_over20_runs", "innings_1_last5_runs",
            "innings_1_total_runs", "innings_1_total_sixes",
            "innings_1_total_fours", "innings_1_total_wickets",
            "innings_1_total_boundaries", "innings_1_highest_score",
            "innings_1_fifties", "innings_1_ducks",
            "innings_1_extras", "innings_1_run_rate",
            "innings_1_50_partnerships", "innings_1_10_over_score",
        ],
        "max_questions": 10,
    },
    {
        "name": "Innings 2 Powerplay",
        "template_type": "in_match",
        "phase_label": "Innings 2 - Powerplay (Overs 1-6)",
        "innings_range": [2],
        "over_start": 1,
        "over_end": 6,
        "answer_deadline_over": 1,  # Must answer before over 1 of innings 2
        "description": "Predict the 2nd innings powerplay!",
        "trigger_filter": "match_end",
        "metric_keywords": [
            "innings_2_pp_runs", "innings_2_pp_wickets", "innings_2_pp_boundaries",
            "innings_2_pp_dots", "innings_2_pp_extras",
            "innings_2_first_over_runs",
        ],
        "max_questions": 10,
    },
    {
        "name": "Innings 2 Death Overs",
        "template_type": "in_match",
        "phase_label": "Innings 2 - Death Overs (16-20)",
        "innings_range": [2],
        "over_start": 16,
        "over_end": 20,
        "answer_deadline_over": 15,
        "description": "Predict the 2nd innings death overs!",
        "trigger_filter": "match_end",
        "metric_keywords": [
            "innings_2_death_runs", "innings_2_death_wickets",
            "innings_2_death_sixes", "innings_2_death_fours",
            "innings_2_last5_runs", "innings_2_last_over_runs",
            "innings_2_over19_runs",
            "innings_2_total_runs", "innings_2_total_sixes",
            "innings_2_total_fours", "innings_2_total_wickets",
            "innings_2_total_boundaries", "innings_2_highest_score",
            "innings_2_fifties", "innings_2_ducks",
            "innings_2_extras", "innings_2_run_rate",
        ],
        "max_questions": 10,
    },
]


def _match_question_to_template(question, config):
    """Check if a question's auto_resolution metric matches a template config."""
    auto_res = question.get("auto_resolution", {})
    if not auto_res:
        return False

    metric = auto_res.get("metric", "")
    trigger = auto_res.get("trigger", "")

    # For full_match: accept match_end and toss triggers
    if config["template_type"] == "full_match":
        # Check if metric matches any full_match keywords
        for kw in config["metric_keywords"]:
            if kw in metric:
                return True
        # Also accept toss questions
        if trigger == "toss":
            return True
        return False

    # For in_match: check trigger and metric keywords
    for kw in config["metric_keywords"]:
        if kw in metric:
            return True
    return False


async def generate_5_templates_for_match(match_id: str, db):
    """
    Generate 5 templates for a match from the question pool.
    Returns summary of created templates.
    """
    match = await db.matches.find_one({"id": match_id}, {"_id": 0})
    if not match:
        raise Exception(f"Match {match_id} not found")

    # Check existing templates
    existing_templates = match.get("templates_assigned", [])
    if len(existing_templates) >= 5:
        return {
            "match_id": match_id,
            "templates_created": 0,
            "message": f"Match already has {len(existing_templates)} templates assigned",
            "template_ids": existing_templates
        }

    # Remove any existing auto-generated templates for this match
    if existing_templates:
        await db.templates.delete_many({"id": {"$in": existing_templates}, "phase_label": {"$ne": None}})

    # Get all active questions from pool
    all_questions = await db.questions.find(
        {"is_active": True, "auto_resolution": {"$ne": None}},
        {"_id": 0}
    ).to_list(length=300)

    if not all_questions:
        raise Exception("No auto-resolution questions found. Run seed-200-questions first.")

    now = utc_now().isoformat()
    created_templates = []
    all_template_ids = []
    used_question_ids = set()

    team_a = match.get("team_a", {}).get("short_name", "TM1")
    team_b = match.get("team_b", {}).get("short_name", "TM2")

    for config in TEMPLATE_CONFIGS:
        # Find matching questions
        matching = [q for q in all_questions if _match_question_to_template(q, config)]

        # Avoid duplicate questions across templates (except full_match can overlap)
        if config["template_type"] != "full_match":
            matching = [q for q in matching if q["id"] not in used_question_ids]

        # Shuffle and limit
        random.shuffle(matching)
        selected = matching[:config["max_questions"]]

        if not selected:
            # If no matching questions, skip this template but try to fill from remaining pool
            remaining = [q for q in all_questions if q["id"] not in used_question_ids]
            random.shuffle(remaining)
            selected = remaining[:5]  # At least 5 filler questions

        if not selected:
            continue

        q_ids = [q["id"] for q in selected]
        total_pts = sum(q.get("points", 50) for q in selected)

        for qid in q_ids:
            used_question_ids.add(qid)

        template_name = f"{team_a} vs {team_b} — {config['name']}"

        template = {
            "id": generate_id(),
            "name": template_name,
            "description": config["description"],
            "match_type": "T20",
            "template_type": config["template_type"],
            "question_ids": q_ids,
            "total_points": total_pts,
            "question_count": len(q_ids),
            "is_active": True,
            "is_default": False,
            "innings_range": config["innings_range"],
            "over_start": config["over_start"],
            "over_end": config["over_end"],
            "answer_deadline_over": config["answer_deadline_over"],
            "phase_label": config["phase_label"],
            "created_at": now,
            "updated_at": now,
        }
        await db.templates.insert_one(template)
        all_template_ids.append(template["id"])
        created_templates.append({
            "id": template["id"],
            "name": template_name,
            "type": config["template_type"],
            "phase": config["phase_label"],
            "questions": len(q_ids),
            "points": total_pts,
        })

    # Assign all templates to match
    await db.matches.update_one(
        {"id": match_id},
        {"$set": {"templates_assigned": all_template_ids, "updated_at": now}}
    )

    return {
        "match_id": match_id,
        "templates_created": len(created_templates),
        "templates": created_templates,
        "total_questions_used": len(used_question_ids),
        "message": f"{len(created_templates)} templates auto-generated for {team_a} vs {team_b}!"
    }
