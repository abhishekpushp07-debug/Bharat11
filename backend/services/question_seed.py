"""
Question Seed Script — IPL Prediction Questions
16 questions ALL in ONE full_match template
Points: Hard=90, Medium=70, Easy=55
ALL text is EXACT copy-paste from user — ZERO modifications.
"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from motor.motor_asyncio import AsyncIOMotorClient
from models.schemas import generate_id, utc_now


# ========================================================================
# ALL 16 QUESTIONS — Single Full Match Template
# First 4 are "पहली पारी" questions, next 12 are "मैच" questions
# ========================================================================
ALL_QUESTIONS = [
    # --- पहली पारी के प्रश्न (Q1-Q4) ---
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
            {"key": "D", "text_hi": "15 या 15 से ज़्यादा", "text_en": "15 or more than 15", "min_value": 15, "max_value": 999},
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
    # --- मैच के प्रश्न (Q5-Q16) ---
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
            {"key": "D", "text_hi": "15 या 15 से ज़्यादा", "text_en": "15 or more than 15", "min_value": 15, "max_value": 999},
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
    client = AsyncIOMotorClient(os.environ.get("MONGO_URL"))
    db = client[os.environ.get("DB_NAME", "crickpredict")]
    now = utc_now().isoformat()

    # Clear existing questions and templates
    await db.questions.delete_many({})
    await db.templates.delete_many({})
    print("Cleared existing questions and templates")

    all_question_ids = []

    print("\n--- ALL 16 QUESTIONS (Full Match Template) ---")
    for i, q_data in enumerate(ALL_QUESTIONS, 1):
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
                "resolution_trigger": q_data["evaluation_rules"]["resolution_trigger"],
            },
            "created_at": now,
            "updated_at": now,
        }
        await db.questions.insert_one(doc)
        all_question_ids.append(q_id)
        diff_emoji = {"easy": "E55", "medium": "M70", "hard": "H90"}[q_data["difficulty"]]
        print(f"  [{diff_emoji}] Q{i}: {q_data['question_text_hi']}")

    # Create SINGLE full_match template with ALL 16 questions
    total_points = sum(q["points"] for q in ALL_QUESTIONS)
    t_id = generate_id()
    await db.templates.insert_one({
        "id": t_id,
        "name": "Full Match Predictions",
        "description": "आज के मैच के लिए सभी प्रश्न",
        "match_type": "t20",
        "template_type": "full_match",
        "question_ids": all_question_ids,
        "total_points": total_points,
        "is_active": True,
        "is_default": True,
        "innings_range": [1, 2],
        "phase_label": "Full Match",
        "created_at": now,
        "updated_at": now,
    })
    print(f"\n--- TEMPLATE ---")
    print(f"  'Full Match Predictions' (full_match) — {len(all_question_ids)} questions, {total_points} total pts")

    # Summary
    easy_count = sum(1 for q in ALL_QUESTIONS if q["difficulty"] == "easy")
    medium_count = sum(1 for q in ALL_QUESTIONS if q["difficulty"] == "medium")
    hard_count = sum(1 for q in ALL_QUESTIONS if q["difficulty"] == "hard")

    print(f"\n=== SEED COMPLETE ===")
    print(f"Total Questions: {len(ALL_QUESTIONS)}")
    print(f"  Easy  (55 pts): {easy_count}")
    print(f"  Medium(70 pts): {medium_count}")
    print(f"  Hard  (90 pts): {hard_count}")
    print(f"Total Points: {total_points}")
    print(f"Templates: 1 (Full Match — ALL 16 questions)")

    client.close()


def generate_expanded_pool(count=200):
    """
    Generate a massive bilingual (Hindi+English) question pool for T20 cricket.
    Categories: batting, bowling, match, death_overs, powerplay, player_performance, special
    Difficulty: easy=55pts, medium=70pts, hard=90pts
    """
    import random

    QUESTION_TEMPLATES = [
        # ============================
        # BATTING — Innings Runs
        # ============================
        {
            "question_text_hi": "पहली पारी में कुल कितने रन बनेंगे?",
            "question_text_en": "How many total runs will be scored in the first innings?",
            "category": "batting", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "150 से कम", "text_en": "Less than 150", "min_value": 0, "max_value": 149},
                {"key": "B", "text_hi": "150-170", "text_en": "150-170", "min_value": 150, "max_value": 170},
                {"key": "C", "text_hi": "171-190", "text_en": "171-190", "min_value": 171, "max_value": 190},
                {"key": "D", "text_hi": "190 से ज़्यादा", "text_en": "More than 190", "min_value": 191, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_total_runs", "resolution_trigger": "innings_1_end"},
        },
        {
            "question_text_hi": "पहली पारी में कितने रन बनेंगे? (High Scoring Pitch)",
            "question_text_en": "How many runs in first innings? (High scoring pitch)",
            "category": "batting", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "180 से कम", "text_en": "Less than 180", "min_value": 0, "max_value": 179},
                {"key": "B", "text_hi": "180-195", "text_en": "180-195", "min_value": 180, "max_value": 195},
                {"key": "C", "text_hi": "196-210", "text_en": "196-210", "min_value": 196, "max_value": 210},
                {"key": "D", "text_hi": "210 से ज़्यादा", "text_en": "More than 210", "min_value": 211, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_total_runs", "resolution_trigger": "innings_1_end"},
        },
        {
            "question_text_hi": "दूसरी पारी में कुल कितने रन बनेंगे?",
            "question_text_en": "How many total runs will be scored in the second innings?",
            "category": "batting", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "140 से कम", "text_en": "Less than 140", "min_value": 0, "max_value": 139},
                {"key": "B", "text_hi": "140-165", "text_en": "140-165", "min_value": 140, "max_value": 165},
                {"key": "C", "text_hi": "166-185", "text_en": "166-185", "min_value": 166, "max_value": 185},
                {"key": "D", "text_hi": "185 से ज़्यादा", "text_en": "More than 185", "min_value": 186, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_2_total_runs", "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "दोनों पारियों को मिलाकर कुल कितने रन बनेंगे?",
            "question_text_en": "How many total runs will be scored in both innings combined?",
            "category": "batting", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "320 से कम", "text_en": "Less than 320", "min_value": 0, "max_value": 319},
                {"key": "B", "text_hi": "320-350", "text_en": "320-350", "min_value": 320, "max_value": 350},
                {"key": "C", "text_hi": "351-380", "text_en": "351-380", "min_value": 351, "max_value": 380},
                {"key": "D", "text_hi": "380 से ज़्यादा", "text_en": "More than 380", "min_value": 381, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "match_total_runs", "resolution_trigger": "match_end"},
        },
        # ============================
        # BATTING — Sixes
        # ============================
        {
            "question_text_hi": "पहली पारी में कितने छक्के लगेंगे?",
            "question_text_en": "How many sixes will be hit in the first innings?",
            "category": "batting", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "5 से कम", "text_en": "Less than 5", "min_value": 0, "max_value": 4},
                {"key": "B", "text_hi": "5-8", "text_en": "5-8", "min_value": 5, "max_value": 8},
                {"key": "C", "text_hi": "9-12", "text_en": "9-12", "min_value": 9, "max_value": 12},
                {"key": "D", "text_hi": "13 या ज़्यादा", "text_en": "13 or more", "min_value": 13, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_total_sixes", "resolution_trigger": "innings_1_end"},
        },
        {
            "question_text_hi": "दूसरी पारी में कितने छक्के लगेंगे?",
            "question_text_en": "How many sixes will be hit in the second innings?",
            "category": "batting", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "5 से कम", "text_en": "Less than 5", "min_value": 0, "max_value": 4},
                {"key": "B", "text_hi": "5-8", "text_en": "5-8", "min_value": 5, "max_value": 8},
                {"key": "C", "text_hi": "9-12", "text_en": "9-12", "min_value": 9, "max_value": 12},
                {"key": "D", "text_hi": "13 या ज़्यादा", "text_en": "13 or more", "min_value": 13, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_2_total_sixes", "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "पूरे मैच में कुल कितने छक्के लगेंगे?",
            "question_text_en": "How many total sixes will be hit in the entire match?",
            "category": "batting", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "10 से कम", "text_en": "Less than 10", "min_value": 0, "max_value": 9},
                {"key": "B", "text_hi": "10-15", "text_en": "10-15", "min_value": 10, "max_value": 15},
                {"key": "C", "text_hi": "16-22", "text_en": "16-22", "min_value": 16, "max_value": 22},
                {"key": "D", "text_hi": "23 या ज़्यादा", "text_en": "23 or more", "min_value": 23, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "match_total_sixes", "resolution_trigger": "match_end"},
        },
        # ============================
        # BATTING — Fours
        # ============================
        {
            "question_text_hi": "पहली पारी में कितने चौके लगेंगे?",
            "question_text_en": "How many fours will be hit in the first innings?",
            "category": "batting", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "10 से कम", "text_en": "Less than 10", "min_value": 0, "max_value": 9},
                {"key": "B", "text_hi": "10-14", "text_en": "10-14", "min_value": 10, "max_value": 14},
                {"key": "C", "text_hi": "15-18", "text_en": "15-18", "min_value": 15, "max_value": 18},
                {"key": "D", "text_hi": "19 या ज़्यादा", "text_en": "19 or more", "min_value": 19, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_total_fours", "resolution_trigger": "innings_1_end"},
        },
        {
            "question_text_hi": "दूसरी पारी में कितने चौके लगेंगे?",
            "question_text_en": "How many fours will be hit in the second innings?",
            "category": "batting", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "10 से कम", "text_en": "Less than 10", "min_value": 0, "max_value": 9},
                {"key": "B", "text_hi": "10-14", "text_en": "10-14", "min_value": 10, "max_value": 14},
                {"key": "C", "text_hi": "15-18", "text_en": "15-18", "min_value": 15, "max_value": 18},
                {"key": "D", "text_hi": "19 या ज़्यादा", "text_en": "19 or more", "min_value": 19, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_2_total_fours", "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "पूरे मैच में कुल कितने चौके लगेंगे?",
            "question_text_en": "How many total fours will be hit in the entire match?",
            "category": "batting", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "20 से कम", "text_en": "Less than 20", "min_value": 0, "max_value": 19},
                {"key": "B", "text_hi": "20-28", "text_en": "20-28", "min_value": 20, "max_value": 28},
                {"key": "C", "text_hi": "29-35", "text_en": "29-35", "min_value": 29, "max_value": 35},
                {"key": "D", "text_hi": "36 या ज़्यादा", "text_en": "36 or more", "min_value": 36, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "match_total_fours", "resolution_trigger": "match_end"},
        },
        # ============================
        # BATTING — Boundaries Combined
        # ============================
        {
            "question_text_hi": "पूरे मैच में कुल कितनी बाउंड्रियाँ (4+6) होंगी?",
            "question_text_en": "How many total boundaries (4s+6s) in the entire match?",
            "category": "batting", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "30 से कम", "text_en": "Less than 30", "min_value": 0, "max_value": 29},
                {"key": "B", "text_hi": "30-40", "text_en": "30-40", "min_value": 30, "max_value": 40},
                {"key": "C", "text_hi": "41-50", "text_en": "41-50", "min_value": 41, "max_value": 50},
                {"key": "D", "text_hi": "51 या ज़्यादा", "text_en": "51 or more", "min_value": 51, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "match_total_boundaries", "resolution_trigger": "match_end"},
        },
        # ============================
        # BOWLING — Wickets
        # ============================
        {
            "question_text_hi": "पहली पारी में कितने विकेट गिरेंगे?",
            "question_text_en": "How many wickets will fall in the first innings?",
            "category": "bowling", "difficulty": "easy", "points": 55,
            "options": [
                {"key": "A", "text_hi": "4 या कम", "text_en": "4 or less", "min_value": 0, "max_value": 4},
                {"key": "B", "text_hi": "5-6", "text_en": "5-6", "min_value": 5, "max_value": 6},
                {"key": "C", "text_hi": "7-8", "text_en": "7-8", "min_value": 7, "max_value": 8},
                {"key": "D", "text_hi": "9-10", "text_en": "9-10", "min_value": 9, "max_value": 10},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_total_wickets", "resolution_trigger": "innings_1_end"},
        },
        {
            "question_text_hi": "दूसरी पारी में कितने विकेट गिरेंगे?",
            "question_text_en": "How many wickets will fall in the second innings?",
            "category": "bowling", "difficulty": "easy", "points": 55,
            "options": [
                {"key": "A", "text_hi": "4 या कम", "text_en": "4 or less", "min_value": 0, "max_value": 4},
                {"key": "B", "text_hi": "5-6", "text_en": "5-6", "min_value": 5, "max_value": 6},
                {"key": "C", "text_hi": "7-8", "text_en": "7-8", "min_value": 7, "max_value": 8},
                {"key": "D", "text_hi": "9-10", "text_en": "9-10", "min_value": 9, "max_value": 10},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_2_total_wickets", "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "पूरे मैच में कुल कितने विकेट गिरेंगे?",
            "question_text_en": "How many total wickets will fall in the entire match?",
            "category": "bowling", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "10 से कम", "text_en": "Less than 10", "min_value": 0, "max_value": 9},
                {"key": "B", "text_hi": "10-13", "text_en": "10-13", "min_value": 10, "max_value": 13},
                {"key": "C", "text_hi": "14-16", "text_en": "14-16", "min_value": 14, "max_value": 16},
                {"key": "D", "text_hi": "17 या ज़्यादा", "text_en": "17 or more", "min_value": 17, "max_value": 20},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "match_total_wickets", "resolution_trigger": "match_end"},
        },
        # ============================
        # BOWLING — Dot Balls & Extras
        # ============================
        {
            "question_text_hi": "पहली पारी में कितनी डॉट बॉल होंगी?",
            "question_text_en": "How many dot balls in the first innings?",
            "category": "bowling", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "35 से कम", "text_en": "Less than 35", "min_value": 0, "max_value": 34},
                {"key": "B", "text_hi": "35-45", "text_en": "35-45", "min_value": 35, "max_value": 45},
                {"key": "C", "text_hi": "46-55", "text_en": "46-55", "min_value": 46, "max_value": 55},
                {"key": "D", "text_hi": "56 या ज़्यादा", "text_en": "56 or more", "min_value": 56, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_dot_balls", "resolution_trigger": "innings_1_end"},
        },
        {
            "question_text_hi": "पूरे मैच में कुल कितने एक्स्ट्रा होंगे?",
            "question_text_en": "How many total extras in the entire match?",
            "category": "special", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "12 या कम", "text_en": "12 or less", "min_value": 0, "max_value": 12},
                {"key": "B", "text_hi": "13-18", "text_en": "13-18", "min_value": 13, "max_value": 18},
                {"key": "C", "text_hi": "19-25", "text_en": "19-25", "min_value": 19, "max_value": 25},
                {"key": "D", "text_hi": "26 या ज़्यादा", "text_en": "26 or more", "min_value": 26, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "match_total_extras", "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "पहली पारी में कितने एक्स्ट्रा (Wide+NB) होंगे?",
            "question_text_en": "How many extras (Wide+No Ball) in the first innings?",
            "category": "bowling", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "5 या कम", "text_en": "5 or less", "min_value": 0, "max_value": 5},
                {"key": "B", "text_hi": "6-9", "text_en": "6-9", "min_value": 6, "max_value": 9},
                {"key": "C", "text_hi": "10-14", "text_en": "10-14", "min_value": 10, "max_value": 14},
                {"key": "D", "text_hi": "15 या ज़्यादा", "text_en": "15 or more", "min_value": 15, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_extras", "resolution_trigger": "innings_1_end"},
        },
        {
            "question_text_hi": "पहली पारी में कितने वाइड बॉल होंगे?",
            "question_text_en": "How many wide balls in the first innings?",
            "category": "bowling", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "3 या कम", "text_en": "3 or less", "min_value": 0, "max_value": 3},
                {"key": "B", "text_hi": "4-6", "text_en": "4-6", "min_value": 4, "max_value": 6},
                {"key": "C", "text_hi": "7-9", "text_en": "7-9", "min_value": 7, "max_value": 9},
                {"key": "D", "text_hi": "10 या ज़्यादा", "text_en": "10 or more", "min_value": 10, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_wides", "resolution_trigger": "innings_1_end"},
        },
        # ============================
        # POWERPLAY (Overs 1-6)
        # ============================
        {
            "question_text_hi": "पहली पारी के पावरप्ले (1-6 ओवर) में कितने रन बनेंगे?",
            "question_text_en": "How many runs in the first innings powerplay (overs 1-6)?",
            "category": "powerplay", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "40 से कम", "text_en": "Less than 40", "min_value": 0, "max_value": 39},
                {"key": "B", "text_hi": "40-50", "text_en": "40-50", "min_value": 40, "max_value": 50},
                {"key": "C", "text_hi": "51-60", "text_en": "51-60", "min_value": 51, "max_value": 60},
                {"key": "D", "text_hi": "61 या ज़्यादा", "text_en": "61 or more", "min_value": 61, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_powerplay_runs", "resolution_trigger": "over_6_end"},
        },
        {
            "question_text_hi": "दूसरी पारी के पावरप्ले में कितने रन बनेंगे?",
            "question_text_en": "How many runs in the second innings powerplay (overs 1-6)?",
            "category": "powerplay", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "35 से कम", "text_en": "Less than 35", "min_value": 0, "max_value": 34},
                {"key": "B", "text_hi": "35-45", "text_en": "35-45", "min_value": 35, "max_value": 45},
                {"key": "C", "text_hi": "46-55", "text_en": "46-55", "min_value": 46, "max_value": 55},
                {"key": "D", "text_hi": "56 या ज़्यादा", "text_en": "56 or more", "min_value": 56, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_2_powerplay_runs", "resolution_trigger": "over_6_end"},
        },
        {
            "question_text_hi": "पहली पारी के पावरप्ले में कितने विकेट गिरेंगे?",
            "question_text_en": "How many wickets in the first innings powerplay?",
            "category": "powerplay", "difficulty": "easy", "points": 55,
            "options": [
                {"key": "A", "text_hi": "0", "text_en": "0", "min_value": 0, "max_value": 0},
                {"key": "B", "text_hi": "1", "text_en": "1", "min_value": 1, "max_value": 1},
                {"key": "C", "text_hi": "2", "text_en": "2", "min_value": 2, "max_value": 2},
                {"key": "D", "text_hi": "3 या ज़्यादा", "text_en": "3 or more", "min_value": 3, "max_value": 10},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_powerplay_wickets", "resolution_trigger": "over_6_end"},
        },
        {
            "question_text_hi": "दूसरी पारी के पावरप्ले में कितने विकेट गिरेंगे?",
            "question_text_en": "How many wickets in the second innings powerplay?",
            "category": "powerplay", "difficulty": "easy", "points": 55,
            "options": [
                {"key": "A", "text_hi": "0", "text_en": "0", "min_value": 0, "max_value": 0},
                {"key": "B", "text_hi": "1", "text_en": "1", "min_value": 1, "max_value": 1},
                {"key": "C", "text_hi": "2", "text_en": "2", "min_value": 2, "max_value": 2},
                {"key": "D", "text_hi": "3 या ज़्यादा", "text_en": "3 or more", "min_value": 3, "max_value": 10},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_2_powerplay_wickets", "resolution_trigger": "over_6_end"},
        },
        {
            "question_text_hi": "पहली पारी के पावरप्ले में कितने छक्के लगेंगे?",
            "question_text_en": "How many sixes in the first innings powerplay?",
            "category": "powerplay", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "0-1", "text_en": "0-1", "min_value": 0, "max_value": 1},
                {"key": "B", "text_hi": "2-3", "text_en": "2-3", "min_value": 2, "max_value": 3},
                {"key": "C", "text_hi": "4-5", "text_en": "4-5", "min_value": 4, "max_value": 5},
                {"key": "D", "text_hi": "6 या ज़्यादा", "text_en": "6 or more", "min_value": 6, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_powerplay_sixes", "resolution_trigger": "over_6_end"},
        },
        # ============================
        # DEATH OVERS (Overs 16-20)
        # ============================
        {
            "question_text_hi": "पहली पारी के डेथ ओवरों (16-20) में कितने रन बनेंगे?",
            "question_text_en": "How many runs in the first innings death overs (16-20)?",
            "category": "death_overs", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "50 से कम", "text_en": "Less than 50", "min_value": 0, "max_value": 49},
                {"key": "B", "text_hi": "50-65", "text_en": "50-65", "min_value": 50, "max_value": 65},
                {"key": "C", "text_hi": "66-80", "text_en": "66-80", "min_value": 66, "max_value": 80},
                {"key": "D", "text_hi": "81 या ज़्यादा", "text_en": "81 or more", "min_value": 81, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_death_runs", "resolution_trigger": "innings_1_end"},
        },
        {
            "question_text_hi": "दूसरी पारी के डेथ ओवरों (16-20) में कितने रन बनेंगे?",
            "question_text_en": "How many runs in the second innings death overs (16-20)?",
            "category": "death_overs", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "45 से कम", "text_en": "Less than 45", "min_value": 0, "max_value": 44},
                {"key": "B", "text_hi": "45-60", "text_en": "45-60", "min_value": 45, "max_value": 60},
                {"key": "C", "text_hi": "61-75", "text_en": "61-75", "min_value": 61, "max_value": 75},
                {"key": "D", "text_hi": "76 या ज़्यादा", "text_en": "76 or more", "min_value": 76, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_2_death_runs", "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "पहली पारी के डेथ ओवरों (16-20) में कितने विकेट गिरेंगे?",
            "question_text_en": "How many wickets in first innings death overs (16-20)?",
            "category": "death_overs", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "0-1", "text_en": "0-1", "min_value": 0, "max_value": 1},
                {"key": "B", "text_hi": "2-3", "text_en": "2-3", "min_value": 2, "max_value": 3},
                {"key": "C", "text_hi": "4", "text_en": "4", "min_value": 4, "max_value": 4},
                {"key": "D", "text_hi": "5 या ज़्यादा", "text_en": "5 or more", "min_value": 5, "max_value": 10},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_death_wickets", "resolution_trigger": "innings_1_end"},
        },
        {
            "question_text_hi": "डेथ ओवरों में कितने छक्के लगेंगे (दोनों पारियाँ)?",
            "question_text_en": "How many sixes in death overs (both innings combined)?",
            "category": "death_overs", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "4 से कम", "text_en": "Less than 4", "min_value": 0, "max_value": 3},
                {"key": "B", "text_hi": "4-7", "text_en": "4-7", "min_value": 4, "max_value": 7},
                {"key": "C", "text_hi": "8-11", "text_en": "8-11", "min_value": 8, "max_value": 11},
                {"key": "D", "text_hi": "12 या ज़्यादा", "text_en": "12 or more", "min_value": 12, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "death_overs_total_sixes", "resolution_trigger": "match_end"},
        },
        # ============================
        # MIDDLE OVERS (Overs 7-15)
        # ============================
        {
            "question_text_hi": "पहली पारी के मिडिल ओवरों (7-15) में कितने रन बनेंगे?",
            "question_text_en": "How many runs in first innings middle overs (7-15)?",
            "category": "batting", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "60 से कम", "text_en": "Less than 60", "min_value": 0, "max_value": 59},
                {"key": "B", "text_hi": "60-75", "text_en": "60-75", "min_value": 60, "max_value": 75},
                {"key": "C", "text_hi": "76-90", "text_en": "76-90", "min_value": 76, "max_value": 90},
                {"key": "D", "text_hi": "91 या ज़्यादा", "text_en": "91 or more", "min_value": 91, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_middle_runs", "resolution_trigger": "over_15_end"},
        },
        {
            "question_text_hi": "दूसरी पारी के मिडिल ओवरों (7-15) में कितने रन बनेंगे?",
            "question_text_en": "How many runs in second innings middle overs (7-15)?",
            "category": "batting", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "55 से कम", "text_en": "Less than 55", "min_value": 0, "max_value": 54},
                {"key": "B", "text_hi": "55-70", "text_en": "55-70", "min_value": 55, "max_value": 70},
                {"key": "C", "text_hi": "71-85", "text_en": "71-85", "min_value": 71, "max_value": 85},
                {"key": "D", "text_hi": "86 या ज़्यादा", "text_en": "86 or more", "min_value": 86, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_2_middle_runs", "resolution_trigger": "over_15_end"},
        },
        # ============================
        # MATCH OUTCOME
        # ============================
        {
            "question_text_hi": "मैच कौन जीतेगा?",
            "question_text_en": "Who will win the match?",
            "category": "match", "difficulty": "easy", "points": 55,
            "options": [
                {"key": "A", "text_hi": "टीम A (पहले बैट)", "text_en": "Team A (batting first)"},
                {"key": "B", "text_hi": "टीम B (चेजिंग)", "text_en": "Team B (chasing)"},
            ],
            "evaluation_rules": {"type": "exact_match", "metric": "match_winner", "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "टॉस कौन जीतेगा?",
            "question_text_en": "Who will win the toss?",
            "category": "match", "difficulty": "easy", "points": 55,
            "options": [
                {"key": "A", "text_hi": "टीम A", "text_en": "Team A"},
                {"key": "B", "text_hi": "टीम B", "text_en": "Team B"},
            ],
            "evaluation_rules": {"type": "exact_match", "metric": "toss_winner", "resolution_trigger": "toss_done"},
        },
        {
            "question_text_hi": "टॉस जीतने वाली टीम क्या करेगी?",
            "question_text_en": "What will the toss winner choose?",
            "category": "match", "difficulty": "easy", "points": 55,
            "options": [
                {"key": "A", "text_hi": "बैटिंग", "text_en": "Batting"},
                {"key": "B", "text_hi": "बॉलिंग", "text_en": "Bowling"},
            ],
            "evaluation_rules": {"type": "exact_match", "metric": "toss_decision", "resolution_trigger": "toss_done"},
        },
        {
            "question_text_hi": "मैच कितने रनों के अंतर से जीता जाएगा?",
            "question_text_en": "By how many runs will the match be won (if batting first wins)?",
            "category": "match", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "10 से कम", "text_en": "Less than 10", "min_value": 0, "max_value": 9},
                {"key": "B", "text_hi": "10-25", "text_en": "10-25", "min_value": 10, "max_value": 25},
                {"key": "C", "text_hi": "26-40", "text_en": "26-40", "min_value": 26, "max_value": 40},
                {"key": "D", "text_hi": "41 या ज़्यादा / विकेट से जीत", "text_en": "41+ or won by wickets", "min_value": 41, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "win_margin_runs", "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "क्या मैच सुपर ओवर तक जाएगा?",
            "question_text_en": "Will the match go to a Super Over?",
            "category": "match", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
                {"key": "B", "text_hi": "नहीं", "text_en": "No"},
            ],
            "evaluation_rules": {"type": "boolean_match", "metric": "is_super_over", "comparator": "==", "threshold": 1, "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "क्या चेज़ करने वाली टीम जीतेगी?",
            "question_text_en": "Will the chasing team win?",
            "category": "match", "difficulty": "easy", "points": 55,
            "options": [
                {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
                {"key": "B", "text_hi": "नहीं", "text_en": "No"},
            ],
            "evaluation_rules": {"type": "boolean_match", "metric": "chasing_team_wins", "comparator": "==", "threshold": 1, "resolution_trigger": "match_end"},
        },
        # ============================
        # PLAYER PERFORMANCE
        # ============================
        {
            "question_text_hi": "क्या कोई बल्लेबाज़ शतक बनाएगा?",
            "question_text_en": "Will any batsman score a century?",
            "category": "player_performance", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
                {"key": "B", "text_hi": "नहीं", "text_en": "No"},
            ],
            "evaluation_rules": {"type": "boolean_match", "metric": "highest_individual_score", "comparator": ">=", "threshold": 100, "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "क्या कोई बल्लेबाज़ 75+ रन बनाएगा?",
            "question_text_en": "Will any batsman score 75+ runs?",
            "category": "player_performance", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
                {"key": "B", "text_hi": "नहीं", "text_en": "No"},
            ],
            "evaluation_rules": {"type": "boolean_match", "metric": "highest_individual_score", "comparator": ">=", "threshold": 75, "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "क्या 3 या ज़्यादा बल्लेबाज़ 40+ रन बनाएंगे?",
            "question_text_en": "Will 3 or more batsmen score 40+ runs?",
            "category": "player_performance", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
                {"key": "B", "text_hi": "नहीं", "text_en": "No"},
            ],
            "evaluation_rules": {"type": "boolean_match", "metric": "batsmen_with_40plus", "comparator": ">=", "threshold": 3, "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "क्या कोई बल्लेबाज़ 5+ छक्के लगाएगा?",
            "question_text_en": "Will any single batsman hit 5+ sixes?",
            "category": "player_performance", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
                {"key": "B", "text_hi": "नहीं", "text_en": "No"},
            ],
            "evaluation_rules": {"type": "boolean_match", "metric": "max_individual_sixes", "comparator": ">=", "threshold": 5, "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "क्या कोई बॉलर 3+ विकेट लेगा?",
            "question_text_en": "Will any bowler take 3+ wickets?",
            "category": "player_performance", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
                {"key": "B", "text_hi": "नहीं", "text_en": "No"},
            ],
            "evaluation_rules": {"type": "boolean_match", "metric": "max_individual_wickets", "comparator": ">=", "threshold": 3, "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "क्या कोई बॉलर 4+ विकेट लेगा?",
            "question_text_en": "Will any bowler take 4+ wickets?",
            "category": "player_performance", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
                {"key": "B", "text_hi": "नहीं", "text_en": "No"},
            ],
            "evaluation_rules": {"type": "boolean_match", "metric": "max_individual_wickets", "comparator": ">=", "threshold": 4, "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "क्या 4 बॉलर 2+ विकेट लेंगे?",
            "question_text_en": "Will 4 bowlers take 2+ wickets each?",
            "category": "bowling", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
                {"key": "B", "text_hi": "नहीं", "text_en": "No"},
            ],
            "evaluation_rules": {"type": "boolean_match", "metric": "bowlers_with_2plus_wickets", "comparator": ">=", "threshold": 4, "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "मैच में सबसे ज़्यादा रन कौन बनाएगा — ओपनर या मिडल ऑर्डर?",
            "question_text_en": "Who will score the most runs - opener or middle order?",
            "category": "player_performance", "difficulty": "easy", "points": 55,
            "options": [
                {"key": "A", "text_hi": "ओपनर (1-3)", "text_en": "Opener (1-3)"},
                {"key": "B", "text_hi": "मिडल ऑर्डर (4-7)", "text_en": "Middle Order (4-7)"},
            ],
            "evaluation_rules": {"type": "exact_match", "metric": "top_scorer_position", "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "मैच का टॉप स्कोरर कितने रन बनाएगा?",
            "question_text_en": "How many runs will the top scorer of the match make?",
            "category": "player_performance", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "40 से कम", "text_en": "Less than 40", "min_value": 0, "max_value": 39},
                {"key": "B", "text_hi": "40-60", "text_en": "40-60", "min_value": 40, "max_value": 60},
                {"key": "C", "text_hi": "61-80", "text_en": "61-80", "min_value": 61, "max_value": 80},
                {"key": "D", "text_hi": "81 या ज़्यादा", "text_en": "81 or more", "min_value": 81, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "highest_individual_score", "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "मैच में सबसे ज़्यादा विकेट लेने वाले बॉलर की इकॉनमी रेट कितनी होगी?",
            "question_text_en": "What will be the economy rate of the highest wicket-taker?",
            "category": "bowling", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "7 से कम", "text_en": "Less than 7", "min_value": 0, "max_value": 6.99},
                {"key": "B", "text_hi": "7-8.5", "text_en": "7-8.5", "min_value": 7, "max_value": 8.5},
                {"key": "C", "text_hi": "8.5-10", "text_en": "8.5-10", "min_value": 8.51, "max_value": 10},
                {"key": "D", "text_hi": "10 से ज़्यादा", "text_en": "More than 10", "min_value": 10.01, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "top_wicket_taker_economy", "resolution_trigger": "match_end"},
        },
        # ============================
        # SPECIAL / MILESTONES
        # ============================
        {
            "question_text_hi": "क्या मैच में कोई हैट-ट्रिक होगी?",
            "question_text_en": "Will there be a hat-trick in the match?",
            "category": "special", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
                {"key": "B", "text_hi": "नहीं", "text_en": "No"},
            ],
            "evaluation_rules": {"type": "boolean_match", "metric": "has_hat_trick", "comparator": "==", "threshold": 1, "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "क्या मैच में कोई मेडन ओवर होगा?",
            "question_text_en": "Will there be a maiden over in the match?",
            "category": "special", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
                {"key": "B", "text_hi": "नहीं", "text_en": "No"},
            ],
            "evaluation_rules": {"type": "boolean_match", "metric": "has_maiden_over", "comparator": "==", "threshold": 1, "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "क्या पहले ओवर में विकेट गिरेगा?",
            "question_text_en": "Will a wicket fall in the first over?",
            "category": "special", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
                {"key": "B", "text_hi": "नहीं", "text_en": "No"},
            ],
            "evaluation_rules": {"type": "boolean_match", "metric": "wicket_in_first_over", "comparator": "==", "threshold": 1, "resolution_trigger": "over_1_end"},
        },
        {
            "question_text_hi": "पहले ओवर में कितने रन बनेंगे?",
            "question_text_en": "How many runs will be scored in the first over?",
            "category": "special", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "0-5", "text_en": "0-5", "min_value": 0, "max_value": 5},
                {"key": "B", "text_hi": "6-10", "text_en": "6-10", "min_value": 6, "max_value": 10},
                {"key": "C", "text_hi": "11-15", "text_en": "11-15", "min_value": 11, "max_value": 15},
                {"key": "D", "text_hi": "16 या ज़्यादा", "text_en": "16 or more", "min_value": 16, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "first_over_runs", "resolution_trigger": "over_1_end"},
        },
        {
            "question_text_hi": "आखिरी ओवर (20th) में कितने रन बनेंगे (पहली पारी)?",
            "question_text_en": "How many runs in the last over (20th) of the first innings?",
            "category": "special", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "0-8", "text_en": "0-8", "min_value": 0, "max_value": 8},
                {"key": "B", "text_hi": "9-14", "text_en": "9-14", "min_value": 9, "max_value": 14},
                {"key": "C", "text_hi": "15-20", "text_en": "15-20", "min_value": 15, "max_value": 20},
                {"key": "D", "text_hi": "21 या ज़्यादा", "text_en": "21 or more", "min_value": 21, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_last_over_runs", "resolution_trigger": "innings_1_end"},
        },
        {
            "question_text_hi": "क्या मैच में कोई रन आउट होगा?",
            "question_text_en": "Will there be a run out in the match?",
            "category": "special", "difficulty": "easy", "points": 55,
            "options": [
                {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
                {"key": "B", "text_hi": "नहीं", "text_en": "No"},
            ],
            "evaluation_rules": {"type": "boolean_match", "metric": "has_run_out", "comparator": ">=", "threshold": 1, "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "मैच में कितने कैच आउट होंगे?",
            "question_text_en": "How many catch outs in the match?",
            "category": "special", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "5 से कम", "text_en": "Less than 5", "min_value": 0, "max_value": 4},
                {"key": "B", "text_hi": "5-8", "text_en": "5-8", "min_value": 5, "max_value": 8},
                {"key": "C", "text_hi": "9-12", "text_en": "9-12", "min_value": 9, "max_value": 12},
                {"key": "D", "text_hi": "13 या ज़्यादा", "text_en": "13 or more", "min_value": 13, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "match_catch_outs", "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "मैच में कुल कितनी LBW आउट होंगी?",
            "question_text_en": "How many LBW dismissals in the match?",
            "category": "special", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "0", "text_en": "0", "min_value": 0, "max_value": 0},
                {"key": "B", "text_hi": "1", "text_en": "1", "min_value": 1, "max_value": 1},
                {"key": "C", "text_hi": "2", "text_en": "2", "min_value": 2, "max_value": 2},
                {"key": "D", "text_hi": "3 या ज़्यादा", "text_en": "3 or more", "min_value": 3, "max_value": 10},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "match_lbw_count", "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "पहली पारी का स्ट्राइक रेट (ओवरऑल) कितना होगा?",
            "question_text_en": "What will be the overall strike rate of first innings?",
            "category": "batting", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "120 से कम", "text_en": "Less than 120", "min_value": 0, "max_value": 119.99},
                {"key": "B", "text_hi": "120-140", "text_en": "120-140", "min_value": 120, "max_value": 140},
                {"key": "C", "text_hi": "141-160", "text_en": "141-160", "min_value": 141, "max_value": 160},
                {"key": "D", "text_hi": "161 या ज़्यादा", "text_en": "161 or more", "min_value": 161, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_strike_rate", "resolution_trigger": "innings_1_end"},
        },
        {
            "question_text_hi": "पहली पारी में highest partnership कितने रन की होगी?",
            "question_text_en": "What will be the highest partnership (runs) in the first innings?",
            "category": "batting", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "30 से कम", "text_en": "Less than 30", "min_value": 0, "max_value": 29},
                {"key": "B", "text_hi": "30-50", "text_en": "30-50", "min_value": 30, "max_value": 50},
                {"key": "C", "text_hi": "51-75", "text_en": "51-75", "min_value": 51, "max_value": 75},
                {"key": "D", "text_hi": "76 या ज़्यादा", "text_en": "76 or more", "min_value": 76, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_highest_partnership", "resolution_trigger": "innings_1_end"},
        },
        {
            "question_text_hi": "दूसरी पारी में highest partnership कितने रन की होगी?",
            "question_text_en": "What will be the highest partnership (runs) in the second innings?",
            "category": "batting", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "25 से कम", "text_en": "Less than 25", "min_value": 0, "max_value": 24},
                {"key": "B", "text_hi": "25-45", "text_en": "25-45", "min_value": 25, "max_value": 45},
                {"key": "C", "text_hi": "46-70", "text_en": "46-70", "min_value": 46, "max_value": 70},
                {"key": "D", "text_hi": "71 या ज़्यादा", "text_en": "71 or more", "min_value": 71, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_2_highest_partnership", "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "पहली पारी में 10 ओवर पर स्कोर कितना होगा?",
            "question_text_en": "What will be the score at 10 overs in the first innings?",
            "category": "batting", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "70 से कम", "text_en": "Less than 70", "min_value": 0, "max_value": 69},
                {"key": "B", "text_hi": "70-85", "text_en": "70-85", "min_value": 70, "max_value": 85},
                {"key": "C", "text_hi": "86-100", "text_en": "86-100", "min_value": 86, "max_value": 100},
                {"key": "D", "text_hi": "101 या ज़्यादा", "text_en": "101 or more", "min_value": 101, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_10over_score", "resolution_trigger": "over_10_end"},
        },
        {
            "question_text_hi": "दूसरी पारी में 10 ओवर पर स्कोर कितना होगा?",
            "question_text_en": "What will be the score at 10 overs in the second innings?",
            "category": "batting", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "65 से कम", "text_en": "Less than 65", "min_value": 0, "max_value": 64},
                {"key": "B", "text_hi": "65-80", "text_en": "65-80", "min_value": 65, "max_value": 80},
                {"key": "C", "text_hi": "81-95", "text_en": "81-95", "min_value": 81, "max_value": 95},
                {"key": "D", "text_hi": "96 या ज़्यादा", "text_en": "96 or more", "min_value": 96, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_2_10over_score", "resolution_trigger": "over_10_end"},
        },
        {
            "question_text_hi": "पहले 5 ओवर में कितने छक्के लगेंगे (पहली पारी)?",
            "question_text_en": "How many sixes in the first 5 overs (1st innings)?",
            "category": "powerplay", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "0", "text_en": "0", "min_value": 0, "max_value": 0},
                {"key": "B", "text_hi": "1-2", "text_en": "1-2", "min_value": 1, "max_value": 2},
                {"key": "C", "text_hi": "3-4", "text_en": "3-4", "min_value": 3, "max_value": 4},
                {"key": "D", "text_hi": "5 या ज़्यादा", "text_en": "5 or more", "min_value": 5, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_first5_sixes", "resolution_trigger": "over_5_end"},
        },
        {
            "question_text_hi": "क्या कोई बॉलर अपने 4 ओवर में 20 से कम रन देगा?",
            "question_text_en": "Will any bowler concede less than 20 runs in their 4 overs?",
            "category": "bowling", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
                {"key": "B", "text_hi": "नहीं", "text_en": "No"},
            ],
            "evaluation_rules": {"type": "boolean_match", "metric": "bowler_under_20_runs", "comparator": ">=", "threshold": 1, "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "क्या कोई बॉलर 10+ economy rate से बॉल करेगा?",
            "question_text_en": "Will any bowler have an economy rate of 10+?",
            "category": "bowling", "difficulty": "easy", "points": 55,
            "options": [
                {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
                {"key": "B", "text_hi": "नहीं", "text_en": "No"},
            ],
            "evaluation_rules": {"type": "boolean_match", "metric": "bowler_10plus_economy", "comparator": ">=", "threshold": 1, "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "पहले विकेट की पार्टनरशिप कितने रन की होगी?",
            "question_text_en": "How many runs for the first wicket partnership?",
            "category": "batting", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "15 से कम", "text_en": "Less than 15", "min_value": 0, "max_value": 14},
                {"key": "B", "text_hi": "15-30", "text_en": "15-30", "min_value": 15, "max_value": 30},
                {"key": "C", "text_hi": "31-50", "text_en": "31-50", "min_value": 31, "max_value": 50},
                {"key": "D", "text_hi": "51 या ज़्यादा", "text_en": "51 or more", "min_value": 51, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_first_wicket_partnership", "resolution_trigger": "first_wicket_fall"},
        },
        {
            "question_text_hi": "दूसरी पारी के पहले विकेट की पार्टनरशिप?",
            "question_text_en": "First wicket partnership in 2nd innings?",
            "category": "batting", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "10 से कम", "text_en": "Less than 10", "min_value": 0, "max_value": 9},
                {"key": "B", "text_hi": "10-25", "text_en": "10-25", "min_value": 10, "max_value": 25},
                {"key": "C", "text_hi": "26-45", "text_en": "26-45", "min_value": 26, "max_value": 45},
                {"key": "D", "text_hi": "46 या ज़्यादा", "text_en": "46 or more", "min_value": 46, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_2_first_wicket_partnership", "resolution_trigger": "first_wicket_fall"},
        },
        {
            "question_text_hi": "क्या पहली पारी में कोई टीम ऑल आउट होगी?",
            "question_text_en": "Will the batting team be all out in the first innings?",
            "category": "match", "difficulty": "easy", "points": 55,
            "options": [
                {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
                {"key": "B", "text_hi": "नहीं", "text_en": "No"},
            ],
            "evaluation_rules": {"type": "boolean_match", "metric": "innings_1_all_out", "comparator": "==", "threshold": 1, "resolution_trigger": "innings_1_end"},
        },
        {
            "question_text_hi": "क्या दूसरी पारी में चेज़ करने वाली टीम ऑल आउट होगी?",
            "question_text_en": "Will the chasing team be all out in the second innings?",
            "category": "match", "difficulty": "easy", "points": 55,
            "options": [
                {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
                {"key": "B", "text_hi": "नहीं", "text_en": "No"},
            ],
            "evaluation_rules": {"type": "boolean_match", "metric": "innings_2_all_out", "comparator": "==", "threshold": 1, "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "मैच में कुल कितनी नो बॉल होंगी?",
            "question_text_en": "How many no balls in the entire match?",
            "category": "bowling", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "0-2", "text_en": "0-2", "min_value": 0, "max_value": 2},
                {"key": "B", "text_hi": "3-5", "text_en": "3-5", "min_value": 3, "max_value": 5},
                {"key": "C", "text_hi": "6-8", "text_en": "6-8", "min_value": 6, "max_value": 8},
                {"key": "D", "text_hi": "9 या ज़्यादा", "text_en": "9 or more", "min_value": 9, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "match_no_balls", "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "दूसरी पारी के डेथ ओवरों (16-20) में कितने विकेट गिरेंगे?",
            "question_text_en": "How many wickets in second innings death overs (16-20)?",
            "category": "death_overs", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "0-1", "text_en": "0-1", "min_value": 0, "max_value": 1},
                {"key": "B", "text_hi": "2-3", "text_en": "2-3", "min_value": 2, "max_value": 3},
                {"key": "C", "text_hi": "4", "text_en": "4", "min_value": 4, "max_value": 4},
                {"key": "D", "text_hi": "5 या ज़्यादा", "text_en": "5 or more", "min_value": 5, "max_value": 10},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_2_death_wickets", "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "10वें ओवर तक पहली पारी में कितने विकेट गिरेंगे?",
            "question_text_en": "How many wickets by the 10th over in the first innings?",
            "category": "batting", "difficulty": "easy", "points": 55,
            "options": [
                {"key": "A", "text_hi": "0-1", "text_en": "0-1", "min_value": 0, "max_value": 1},
                {"key": "B", "text_hi": "2-3", "text_en": "2-3", "min_value": 2, "max_value": 3},
                {"key": "C", "text_hi": "4-5", "text_en": "4-5", "min_value": 4, "max_value": 5},
                {"key": "D", "text_hi": "6 या ज़्यादा", "text_en": "6 or more", "min_value": 6, "max_value": 10},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_wickets_at_10", "resolution_trigger": "over_10_end"},
        },
        {
            "question_text_hi": "क्या मैच में 30 या ज़्यादा छक्के लगेंगे?",
            "question_text_en": "Will there be 30 or more sixes in the match?",
            "category": "batting", "difficulty": "hard", "points": 90,
            "options": [
                {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
                {"key": "B", "text_hi": "नहीं", "text_en": "No"},
            ],
            "evaluation_rules": {"type": "boolean_match", "metric": "match_total_sixes", "comparator": ">=", "threshold": 30, "resolution_trigger": "match_end"},
        },
        {
            "question_text_hi": "15वें ओवर तक पहली पारी में कितने रन होंगे?",
            "question_text_en": "How many runs by the 15th over in the first innings?",
            "category": "batting", "difficulty": "medium", "points": 70,
            "options": [
                {"key": "A", "text_hi": "100 से कम", "text_en": "Less than 100", "min_value": 0, "max_value": 99},
                {"key": "B", "text_hi": "100-120", "text_en": "100-120", "min_value": 100, "max_value": 120},
                {"key": "C", "text_hi": "121-140", "text_en": "121-140", "min_value": 121, "max_value": 140},
                {"key": "D", "text_hi": "141 या ज़्यादा", "text_en": "141 or more", "min_value": 141, "max_value": 999},
            ],
            "evaluation_rules": {"type": "range_match", "metric": "innings_1_15over_score", "resolution_trigger": "over_15_end"},
        },
    ]

    pool = []
    unique_keys = set()

    for i, tmpl in enumerate(QUESTION_TEMPLATES):
        if len(pool) >= count:
            break
        q_id = generate_id()
        key = tmpl["question_text_en"]
        if key in unique_keys:
            continue
        unique_keys.add(key)
        q = {
            "id": q_id,
            "question_text_en": tmpl["question_text_en"],
            "question_text_hi": tmpl["question_text_hi"],
            "category": tmpl["category"],
            "difficulty": tmpl["difficulty"],
            "points": tmpl["points"],
            "options": tmpl["options"],
            "evaluation_rules": tmpl.get("evaluation_rules", {}),
            "auto_resolution": tmpl.get("evaluation_rules", {}),
        }
        pool.append(q)

    # If we need more, generate variants by adjusting ranges
    variants_base = [
        ("batting", "medium", 70, "innings_1_total_runs", "innings_1_end",
         "पहली पारी में {low}-{high} रन बनेंगे?", "Will first innings score be {low}-{high} runs?"),
        ("batting", "medium", 70, "innings_2_total_runs", "match_end",
         "दूसरी पारी में {low}-{high} रन बनेंगे?", "Will second innings score be {low}-{high} runs?"),
        ("bowling", "easy", 55, "innings_1_total_wickets", "innings_1_end",
         "पहली पारी में {low}+ विकेट गिरेंगे?", "Will {low}+ wickets fall in first innings?"),
        ("batting", "hard", 90, "match_total_sixes", "match_end",
         "मैच में कुल {low}-{high} छक्के लगेंगे?", "Will total match sixes be {low}-{high}?"),
        ("death_overs", "medium", 70, "innings_1_death_runs", "innings_1_end",
         "पहली पारी डेथ ओवरों में {low}-{high} रन?", "First innings death overs {low}-{high} runs?"),
        ("powerplay", "medium", 70, "innings_1_powerplay_runs", "over_6_end",
         "पहली पारी PP में {low}-{high} रन?", "First innings PP {low}-{high} runs?"),
        ("special", "hard", 90, "match_total_extras", "match_end",
         "मैच में कुल {low}-{high} एक्स्ट्रा?", "Total match extras {low}-{high}?"),
        ("player_performance", "medium", 70, "highest_individual_score", "match_end",
         "टॉप स्कोरर {low}-{high} रन बनाएगा?", "Top scorer will make {low}-{high} runs?"),
    ]

    range_configs = [
        (100, 130), (131, 160), (161, 190), (191, 220),
        (0, 5), (6, 10), (11, 15), (16, 25),
        (30, 50), (51, 70), (71, 90), (91, 120),
    ]

    variant_idx = 0
    while len(pool) < count and variant_idx < 500:
        base = variants_base[variant_idx % len(variants_base)]
        ranges = range_configs[variant_idx % len(range_configs)]
        cat, diff, pts, metric, trigger, hi_tmpl, en_tmpl = base
        low, high = ranges

        q_text_hi = hi_tmpl.format(low=low, high=high)
        q_text_en = en_tmpl.format(low=low, high=high)

        key = q_text_en
        if key in unique_keys:
            variant_idx += 1
            continue
        unique_keys.add(key)

        q = {
            "id": generate_id(),
            "question_text_en": q_text_en,
            "question_text_hi": q_text_hi,
            "category": cat,
            "difficulty": diff,
            "points": pts,
            "options": [
                {"key": "A", "text_hi": "हाँ", "text_en": "Yes"},
                {"key": "B", "text_hi": "नहीं", "text_en": "No"},
            ],
            "evaluation_rules": {
                "type": "boolean_match",
                "metric": metric,
                "comparator": ">=",
                "threshold": low,
                "resolution_trigger": trigger,
            },
            "auto_resolution": {
                "type": "boolean_match",
                "metric": metric,
                "comparator": ">=",
                "threshold": low,
                "resolution_trigger": trigger,
            },
        }
        pool.append(q)
        variant_idx += 1

    random.shuffle(pool)
    return pool[:count]


if __name__ == "__main__":
    asyncio.run(seed_questions())
