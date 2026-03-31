"""
Question Seed Script — IPL Prediction Questions
16 questions with difficulty-based points: Hard=90, Medium=70, Easy=55
2 Templates: "First Innings" (4 questions) + "Full Match" (12 questions)
"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from motor.motor_asyncio import AsyncIOMotorClient
from models.schemas import generate_id, utc_now


FIRST_INNINGS_QUESTIONS = [
    {
        "question_text_hi": "आज पहली पारी में कितने रन बनेंगे?",
        "question_text_en": "How many runs will be scored in today's first innings?",
        "category": "batting",
        "difficulty": "medium",
        "points": 70,
        "options": [
            {"key": "A", "text_hi": "190 से कम", "text_en": "Less than 190", "min_value": 0, "max_value": 189},
            {"key": "B", "text_hi": "190-200", "text_en": "190-200", "min_value": 190, "max_value": 200},
            {"key": "C", "text_hi": "200-210", "text_en": "200-210", "min_value": 201, "max_value": 210},
            {"key": "D", "text_hi": "210 से ज़्यादा", "text_en": "More than 210", "min_value": 211, "max_value": 999},
        ],
        "evaluation_rules": {
            "type": "range_match",
            "metric": "innings_1_total_runs",
            "resolution_trigger": "innings_1_end",
        },
    },
    {
        "question_text_hi": "आज पहली पारी में कितने विकेट गिरेंगे?",
        "question_text_en": "How many wickets will fall in today's first innings?",
        "category": "bowling",
        "difficulty": "easy",
        "points": 55,
        "options": [
            {"key": "A", "text_hi": "5 से कम", "text_en": "Less than 5", "min_value": 0, "max_value": 4},
            {"key": "B", "text_hi": "5 या 6", "text_en": "5 or 6", "min_value": 5, "max_value": 6},
            {"key": "C", "text_hi": "7", "text_en": "7", "min_value": 7, "max_value": 7},
            {"key": "D", "text_hi": "8 या ज़्यादा", "text_en": "8 or more", "min_value": 8, "max_value": 10},
        ],
        "evaluation_rules": {
            "type": "range_match",
            "metric": "innings_1_total_wickets",
            "resolution_trigger": "innings_1_end",
        },
    },
    {
        "question_text_hi": "आज पहली पारी में कितने छक्के लगेंगे?",
        "question_text_en": "How many sixes will be hit in today's first innings?",
        "category": "batting",
        "difficulty": "hard",
        "points": 90,
        "options": [
            {"key": "A", "text_hi": "13 से कम", "text_en": "Less than 13", "min_value": 0, "max_value": 12},
            {"key": "B", "text_hi": "13 या 14", "text_en": "13 or 14", "min_value": 13, "max_value": 14},
            {"key": "C", "text_hi": "15", "text_en": "15", "min_value": 15, "max_value": 15},
            {"key": "D", "text_hi": "15 या 15 से ज़्यादा", "text_en": "15 or more", "min_value": 15, "max_value": 999},
        ],
        "evaluation_rules": {
            "type": "range_match",
            "metric": "innings_1_total_sixes",
            "resolution_trigger": "innings_1_end",
        },
    },
    {
        "question_text_hi": "आज पहली पारी में कितने चौके लगेंगे?",
        "question_text_en": "How many fours will be hit in today's first innings?",
        "category": "batting",
        "difficulty": "hard",
        "points": 90,
        "options": [
            {"key": "A", "text_hi": "14", "text_en": "14", "min_value": 14, "max_value": 14},
            {"key": "B", "text_hi": "15", "text_en": "15", "min_value": 15, "max_value": 15},
            {"key": "C", "text_hi": "16 या 17", "text_en": "16 or 17", "min_value": 16, "max_value": 17},
            {"key": "D", "text_hi": "18 या ज़्यादा", "text_en": "18 or more", "min_value": 18, "max_value": 999},
        ],
        "evaluation_rules": {
            "type": "range_match",
            "metric": "innings_1_total_fours",
            "resolution_trigger": "innings_1_end",
        },
    },
]


FULL_MATCH_QUESTIONS = [
    {
        "question_text_hi": "आज का मैच कौन जीतेगा?",
        "question_text_en": "Who will win today's match?",
        "category": "match",
        "difficulty": "easy",
        "points": 55,
        "options": [
            {"key": "A", "text_hi": "पंजाब किंग्स", "text_en": "Punjab Kings"},
            {"key": "B", "text_hi": "गुजरात टाइटंस", "text_en": "Gujarat Titans"},
        ],
        "evaluation_rules": {
            "type": "exact_match",
            "metric": "match_winner",
            "resolution_trigger": "match_end",
        },
    },
    {
        "question_text_hi": "आज दूसरी पारी के 10.1 से 20 ओवरों में कितने रन बनेंगे?",
        "question_text_en": "How many runs will be scored in overs 10.1 to 20 of today's second innings?",
        "category": "death_overs",
        "difficulty": "hard",
        "points": 90,
        "options": [
            {"key": "A", "text_hi": "100 से कम", "text_en": "Less than 100", "min_value": 0, "max_value": 100},
            {"key": "B", "text_hi": "101-105", "text_en": "101-105", "min_value": 101, "max_value": 105},
            {"key": "C", "text_hi": "106-112", "text_en": "106-112", "min_value": 106, "max_value": 112},
            {"key": "D", "text_hi": "113 या उससे ज़्यादा", "text_en": "113 or more", "min_value": 113, "max_value": 999},
        ],
        "evaluation_rules": {
            "type": "range_match",
            "metric": "innings_2_death_runs",
            "resolution_trigger": "match_end",
        },
    },
    {
        "question_text_hi": "आज दूसरी पारी में कितने छक्के लगेंगे?",
        "question_text_en": "How many sixes will be hit in today's second innings?",
        "category": "batting",
        "difficulty": "hard",
        "points": 90,
        "options": [
            {"key": "A", "text_hi": "13 से कम", "text_en": "Less than 13", "min_value": 0, "max_value": 12},
            {"key": "B", "text_hi": "13 या 14", "text_en": "13 or 14", "min_value": 13, "max_value": 14},
            {"key": "C", "text_hi": "15", "text_en": "15", "min_value": 15, "max_value": 15},
            {"key": "D", "text_hi": "15 या 15 से ज़्यादा", "text_en": "15 or more", "min_value": 15, "max_value": 999},
        ],
        "evaluation_rules": {
            "type": "range_match",
            "metric": "innings_2_total_sixes",
            "resolution_trigger": "match_end",
        },
    },
    {
        "question_text_hi": "आज दूसरी पारी में कितने चौके लगेंगे?",
        "question_text_en": "How many fours will be hit in today's second innings?",
        "category": "batting",
        "difficulty": "hard",
        "points": 90,
        "options": [
            {"key": "A", "text_hi": "14", "text_en": "14", "min_value": 14, "max_value": 14},
            {"key": "B", "text_hi": "15", "text_en": "15", "min_value": 15, "max_value": 15},
            {"key": "C", "text_hi": "16 या 17", "text_en": "16 or 17", "min_value": 16, "max_value": 17},
            {"key": "D", "text_hi": "18 या ज़्यादा", "text_en": "18 or more", "min_value": 18, "max_value": 999},
        ],
        "evaluation_rules": {
            "type": "range_match",
            "metric": "innings_2_total_fours",
            "resolution_trigger": "match_end",
        },
    },
    {
        "question_text_hi": "आज दूसरी पारी में कितने विकेट गिरेंगे?",
        "question_text_en": "How many wickets will fall in today's second innings?",
        "category": "bowling",
        "difficulty": "medium",
        "points": 70,
        "options": [
            {"key": "A", "text_hi": "5 से कम", "text_en": "Less than 5", "min_value": 0, "max_value": 4},
            {"key": "B", "text_hi": "5 या 6", "text_en": "5 or 6", "min_value": 5, "max_value": 6},
            {"key": "C", "text_hi": "7", "text_en": "7", "min_value": 7, "max_value": 7},
            {"key": "D", "text_hi": "8 या ज़्यादा", "text_en": "8 or more", "min_value": 8, "max_value": 10},
        ],
        "evaluation_rules": {
            "type": "range_match",
            "metric": "innings_2_total_wickets",
            "resolution_trigger": "match_end",
        },
    },
    {
        "question_text_hi": "आज क्या 3 बल्लेबाज़ 50 या उससे ज़्यादा रन बनाएंगे?",
        "question_text_en": "Will 3 batsmen score 50 or more runs today?",
        "category": "player_performance",
        "difficulty": "hard",
        "points": 90,
        "options": [
            {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
            {"key": "B", "text_hi": "नहीं", "text_en": "No"},
        ],
        "evaluation_rules": {
            "type": "boolean_match",
            "metric": "batsmen_with_50plus",
            "comparator": ">=",
            "threshold": 3,
            "resolution_trigger": "match_end",
        },
    },
    {
        "question_text_hi": "आज क्या कोई बल्लेबाज़ 80 या उससे ज़्यादा रन बनाएगा?",
        "question_text_en": "Will any batsman score 80 or more runs today?",
        "category": "player_performance",
        "difficulty": "medium",
        "points": 70,
        "options": [
            {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
            {"key": "B", "text_hi": "नहीं", "text_en": "No"},
        ],
        "evaluation_rules": {
            "type": "boolean_match",
            "metric": "highest_individual_score",
            "comparator": ">=",
            "threshold": 80,
            "resolution_trigger": "match_end",
        },
    },
    {
        "question_text_hi": "आज क्या कोई एक बल्लेबाज़ 5 या उससे ज़्यादा छक्के लगाएगा?",
        "question_text_en": "Will any single batsman hit 5 or more sixes today?",
        "category": "player_performance",
        "difficulty": "medium",
        "points": 70,
        "options": [
            {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
            {"key": "B", "text_hi": "नहीं", "text_en": "No"},
        ],
        "evaluation_rules": {
            "type": "boolean_match",
            "metric": "max_individual_sixes",
            "comparator": ">=",
            "threshold": 5,
            "resolution_trigger": "match_end",
        },
    },
    {
        "question_text_hi": "आज क्या 4 गेंदबाज़ कम से कम 2 विकेट लेंगे?",
        "question_text_en": "Will 4 bowlers take at least 2 wickets each today?",
        "category": "bowling",
        "difficulty": "hard",
        "points": 90,
        "options": [
            {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
            {"key": "B", "text_hi": "नहीं", "text_en": "No"},
        ],
        "evaluation_rules": {
            "type": "boolean_match",
            "metric": "bowlers_with_2plus_wickets",
            "comparator": ">=",
            "threshold": 4,
            "resolution_trigger": "match_end",
        },
    },
    {
        "question_text_hi": "आज क्या 3 गेंदबाज़ कम से कम 3 विकेट लेंगे?",
        "question_text_en": "Will 3 bowlers take at least 3 wickets each today?",
        "category": "bowling",
        "difficulty": "hard",
        "points": 90,
        "options": [
            {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
            {"key": "B", "text_hi": "नहीं", "text_en": "No"},
        ],
        "evaluation_rules": {
            "type": "boolean_match",
            "metric": "bowlers_with_3plus_wickets",
            "comparator": ">=",
            "threshold": 3,
            "resolution_trigger": "match_end",
        },
    },
    {
        "question_text_hi": "आज मैच में कुल एक्स्ट्रा कितने होंगे?",
        "question_text_en": "How many total extras will there be in today's match?",
        "category": "special",
        "difficulty": "hard",
        "points": 90,
        "options": [
            {"key": "A", "text_hi": "21 या उससे कम", "text_en": "21 or less", "min_value": 0, "max_value": 21},
            {"key": "B", "text_hi": "22-25", "text_en": "22-25", "min_value": 22, "max_value": 25},
            {"key": "C", "text_hi": "26-30", "text_en": "26-30", "min_value": 26, "max_value": 30},
            {"key": "D", "text_hi": "30 से ज़्यादा", "text_en": "More than 30", "min_value": 31, "max_value": 999},
        ],
        "evaluation_rules": {
            "type": "range_match",
            "metric": "match_total_extras",
            "resolution_trigger": "match_end",
        },
    },
    {
        "question_text_hi": "आज क्या कोई शतक बनेगा?",
        "question_text_en": "Will there be a century today?",
        "category": "player_performance",
        "difficulty": "medium",
        "points": 70,
        "options": [
            {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
            {"key": "B", "text_hi": "नहीं", "text_en": "No"},
        ],
        "evaluation_rules": {
            "type": "boolean_match",
            "metric": "highest_individual_score",
            "comparator": ">=",
            "threshold": 100,
            "resolution_trigger": "match_end",
        },
    },
]


async def seed_questions():
    client = AsyncIOMotorClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"))
    db = client[os.environ.get("DB_NAME", "crickpredict")]
    now = utc_now().isoformat()

    # Clear existing questions and templates
    await db.questions.delete_many({})
    await db.templates.delete_many({})
    print("Cleared existing questions and templates")

    first_innings_ids = []
    full_match_ids = []

    # Seed First Innings Questions
    print("\n--- FIRST INNINGS QUESTIONS ---")
    for i, q_data in enumerate(FIRST_INNINGS_QUESTIONS, 1):
        q_id = generate_id()
        doc = {
            "id": q_id,
            "question_text_en": q_data["question_text_en"],
            "question_text_hi": q_data["question_text_hi"],
            "category": q_data["category"],
            "difficulty": q_data["difficulty"],
            "points": q_data["points"],
            "multiplier": 1.0,
            "is_active": True,
            "options": q_data["options"],
            "evaluation_rules": {
                "type": q_data["evaluation_rules"]["type"],
                "metric": q_data["evaluation_rules"]["metric"],
                "comparator": q_data["evaluation_rules"].get("comparator"),
                "threshold": q_data["evaluation_rules"].get("threshold"),
                "threshold_min": q_data["evaluation_rules"].get("threshold_min"),
                "threshold_max": q_data["evaluation_rules"].get("threshold_max"),
                "resolution_trigger": q_data["evaluation_rules"]["resolution_trigger"],
                "secondary_metric": q_data["evaluation_rules"].get("secondary_metric"),
            },
            "created_at": now,
            "updated_at": now,
        }
        await db.questions.insert_one(doc)
        first_innings_ids.append(q_id)
        diff_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}[q_data["difficulty"]]
        print(f"  {diff_emoji} Q{i}: {q_data['question_text_hi']} [{q_data['difficulty'].upper()} = {q_data['points']} pts]")

    # Seed Full Match Questions
    print("\n--- FULL MATCH QUESTIONS ---")
    for i, q_data in enumerate(FULL_MATCH_QUESTIONS, 1):
        q_id = generate_id()
        doc = {
            "id": q_id,
            "question_text_en": q_data["question_text_en"],
            "question_text_hi": q_data["question_text_hi"],
            "category": q_data["category"],
            "difficulty": q_data["difficulty"],
            "points": q_data["points"],
            "multiplier": 1.0,
            "is_active": True,
            "options": q_data["options"],
            "evaluation_rules": {
                "type": q_data["evaluation_rules"]["type"],
                "metric": q_data["evaluation_rules"]["metric"],
                "comparator": q_data["evaluation_rules"].get("comparator"),
                "threshold": q_data["evaluation_rules"].get("threshold"),
                "threshold_min": q_data["evaluation_rules"].get("threshold_min"),
                "threshold_max": q_data["evaluation_rules"].get("threshold_max"),
                "resolution_trigger": q_data["evaluation_rules"]["resolution_trigger"],
                "secondary_metric": q_data["evaluation_rules"].get("secondary_metric"),
            },
            "created_at": now,
            "updated_at": now,
        }
        await db.questions.insert_one(doc)
        full_match_ids.append(q_id)
        diff_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}[q_data["difficulty"]]
        print(f"  {diff_emoji} Q{i}: {q_data['question_text_hi']} [{q_data['difficulty'].upper()} = {q_data['points']} pts]")

    # Create Templates
    print("\n--- TEMPLATES ---")

    # Template 1: First Innings
    first_innings_total = sum(q["points"] for q in FIRST_INNINGS_QUESTIONS)
    t1_id = generate_id()
    await db.templates.insert_one({
        "id": t1_id,
        "name": "First Innings Predictions",
        "description": "पहली पारी के प्रश्न — Predict first innings outcomes",
        "match_type": "t20",
        "template_type": "in_match",
        "question_ids": first_innings_ids,
        "total_points": first_innings_total,
        "is_active": True,
        "is_default": True,
        "innings_range": [1],
        "over_start": 1,
        "over_end": 20,
        "answer_deadline_over": 1,
        "phase_label": "First Innings",
        "created_at": now,
        "updated_at": now,
    })
    print(f"  Template 1: 'First Innings Predictions' — {len(first_innings_ids)} questions, {first_innings_total} total pts")

    # Template 2: Full Match
    full_match_total = sum(q["points"] for q in FULL_MATCH_QUESTIONS)
    t2_id = generate_id()
    await db.templates.insert_one({
        "id": t2_id,
        "name": "Full Match Predictions",
        "description": "पूरे मैच के प्रश्न — Predict full match outcomes",
        "match_type": "t20",
        "template_type": "full_match",
        "question_ids": full_match_ids,
        "total_points": full_match_total,
        "is_active": True,
        "is_default": True,
        "innings_range": [1, 2],
        "phase_label": "Full Match",
        "created_at": now,
        "updated_at": now,
    })
    print(f"  Template 2: 'Full Match Predictions' — {len(full_match_ids)} questions, {full_match_total} total pts")

    # Summary
    all_questions = FIRST_INNINGS_QUESTIONS + FULL_MATCH_QUESTIONS
    easy_count = sum(1 for q in all_questions if q["difficulty"] == "easy")
    medium_count = sum(1 for q in all_questions if q["difficulty"] == "medium")
    hard_count = sum(1 for q in all_questions if q["difficulty"] == "hard")
    total_pts = first_innings_total + full_match_total

    print(f"\n=== SEED COMPLETE ===")
    print(f"Total Questions: {len(all_questions)}")
    print(f"  Easy (55 pts): {easy_count}")
    print(f"  Medium (70 pts): {medium_count}")
    print(f"  Hard (90 pts): {hard_count}")
    print(f"Total Points: {total_pts}")
    print(f"Templates: 2 (First Innings + Full Match)")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed_questions())
