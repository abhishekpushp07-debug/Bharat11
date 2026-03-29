"""
Database Seeder
Seeds initial data for CrickPredict: questions, templates, sample matches.
"""
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List

from motor.motor_asyncio import AsyncIOMotorClient

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from models.schemas import (
    Question, QuestionOption, EvaluationRules, EvaluationType,
    QuestionCategory, QuestionDifficulty,
    Template, Match, Team, MatchType, MatchStatus,
    Contest, ContestStatus, PrizeDistribution
)


# ==================== SAMPLE QUESTIONS ====================

SAMPLE_QUESTIONS: List[dict] = [
    # Batting Questions
    {
        "question_text_en": "How many total runs will be scored in the first innings?",
        "question_text_hi": "पहली पारी में कुल कितने रन बनेंगे?",
        "category": QuestionCategory.BATTING,
        "options": [
            {"key": "A", "text_en": "Less than 150", "text_hi": "150 से कम", "max_value": 149},
            {"key": "B", "text_en": "150-170", "text_hi": "150-170", "min_value": 150, "max_value": 170},
            {"key": "C", "text_en": "171-190", "text_hi": "171-190", "min_value": 171, "max_value": 190},
            {"key": "D", "text_en": "More than 190", "text_hi": "190 से ज्यादा", "min_value": 191},
        ],
        "points": 70,
        "multiplier": 1.0,
        "evaluation_rules": {
            "type": EvaluationType.RANGE_MATCH,
            "metric": "innings_1_total",
            "resolution_trigger": "innings_end"
        },
        "difficulty": QuestionDifficulty.MEDIUM
    },
    {
        "question_text_en": "Will any player score 50 or more runs?",
        "question_text_hi": "क्या कोई खिलाड़ी 50 या उससे अधिक रन बनाएगा?",
        "category": QuestionCategory.BATTING,
        "options": [
            {"key": "A", "text_en": "Yes", "text_hi": "हाँ"},
            {"key": "B", "text_en": "No", "text_hi": "नहीं"},
        ],
        "points": 60,
        "multiplier": 1.0,
        "evaluation_rules": {
            "type": EvaluationType.BOOLEAN_MATCH,
            "metric": "highest_individual_score",
            "comparator": ">=",
            "threshold": 50,
            "resolution_trigger": "match_end"
        },
        "difficulty": QuestionDifficulty.EASY
    },
    {
        "question_text_en": "Will any player score 70+ runs?",
        "question_text_hi": "क्या कोई खिलाड़ी 70 या उससे अधिक रन बनाएगा?",
        "category": QuestionCategory.BATTING,
        "options": [
            {"key": "A", "text_en": "Yes", "text_hi": "हाँ"},
            {"key": "B", "text_en": "No", "text_hi": "नहीं"},
        ],
        "points": 80,
        "multiplier": 1.5,
        "evaluation_rules": {
            "type": EvaluationType.BOOLEAN_MATCH,
            "metric": "highest_individual_score",
            "comparator": ">=",
            "threshold": 70,
            "resolution_trigger": "match_end"
        },
        "difficulty": QuestionDifficulty.HARD
    },
    
    # Powerplay Questions
    {
        "question_text_en": "How many runs will be scored in the powerplay (overs 1-6)?",
        "question_text_hi": "पावरप्ले (ओवर 1-6) में कितने रन बनेंगे?",
        "category": QuestionCategory.POWERPLAY,
        "options": [
            {"key": "A", "text_en": "Less than 45", "text_hi": "45 से कम", "max_value": 44},
            {"key": "B", "text_en": "45-55", "text_hi": "45-55", "min_value": 45, "max_value": 55},
            {"key": "C", "text_en": "56-65", "text_hi": "56-65", "min_value": 56, "max_value": 65},
            {"key": "D", "text_en": "More than 65", "text_hi": "65 से ज्यादा", "min_value": 66},
        ],
        "points": 65,
        "multiplier": 1.0,
        "evaluation_rules": {
            "type": EvaluationType.RANGE_MATCH,
            "metric": "powerplay_runs",
            "resolution_trigger": "powerplay_end"
        },
        "difficulty": QuestionDifficulty.MEDIUM
    },
    {
        "question_text_en": "How many wickets will fall in the powerplay?",
        "question_text_hi": "पावरप्ले में कितने विकेट गिरेंगे?",
        "category": QuestionCategory.POWERPLAY,
        "options": [
            {"key": "A", "text_en": "0-1", "text_hi": "0-1", "max_value": 1},
            {"key": "B", "text_en": "2", "text_hi": "2", "min_value": 2, "max_value": 2},
            {"key": "C", "text_en": "3", "text_hi": "3", "min_value": 3, "max_value": 3},
            {"key": "D", "text_en": "4 or more", "text_hi": "4 या अधिक", "min_value": 4},
        ],
        "points": 70,
        "multiplier": 1.0,
        "evaluation_rules": {
            "type": EvaluationType.RANGE_MATCH,
            "metric": "powerplay_wickets",
            "resolution_trigger": "powerplay_end"
        },
        "difficulty": QuestionDifficulty.MEDIUM
    },
    
    # Bowling Questions
    {
        "question_text_en": "How many total wickets will fall in the match?",
        "question_text_hi": "पूरे मैच में कुल कितने विकेट गिरेंगे?",
        "category": QuestionCategory.BOWLING,
        "options": [
            {"key": "A", "text_en": "Less than 10", "text_hi": "10 से कम", "max_value": 9},
            {"key": "B", "text_en": "10-13", "text_hi": "10-13", "min_value": 10, "max_value": 13},
            {"key": "C", "text_en": "14-16", "text_hi": "14-16", "min_value": 14, "max_value": 16},
            {"key": "D", "text_en": "17 or more", "text_hi": "17 या अधिक", "min_value": 17},
        ],
        "points": 65,
        "multiplier": 1.0,
        "evaluation_rules": {
            "type": EvaluationType.RANGE_MATCH,
            "metric": "total_wickets",
            "resolution_trigger": "match_end"
        },
        "difficulty": QuestionDifficulty.MEDIUM
    },
    {
        "question_text_en": "Will any bowler take 3 or more wickets?",
        "question_text_hi": "क्या कोई गेंदबाज 3 या उससे अधिक विकेट लेगा?",
        "category": QuestionCategory.BOWLING,
        "options": [
            {"key": "A", "text_en": "Yes", "text_hi": "हाँ"},
            {"key": "B", "text_en": "No", "text_hi": "नहीं"},
        ],
        "points": 75,
        "multiplier": 1.0,
        "evaluation_rules": {
            "type": EvaluationType.BOOLEAN_MATCH,
            "metric": "best_bowling_wickets",
            "comparator": ">=",
            "threshold": 3,
            "resolution_trigger": "match_end"
        },
        "difficulty": QuestionDifficulty.MEDIUM
    },
    
    # Match Questions
    {
        "question_text_en": "Will the chasing team win?",
        "question_text_hi": "क्या पीछा करने वाली टीम जीतेगी?",
        "category": QuestionCategory.MATCH,
        "options": [
            {"key": "A", "text_en": "Yes", "text_hi": "हाँ"},
            {"key": "B", "text_en": "No", "text_hi": "नहीं"},
        ],
        "points": 70,
        "multiplier": 1.0,
        "evaluation_rules": {
            "type": EvaluationType.BOOLEAN_MATCH,
            "metric": "chasing_team_won",
            "comparator": "==",
            "threshold": 1,
            "resolution_trigger": "match_end"
        },
        "difficulty": QuestionDifficulty.EASY
    },
    {
        "question_text_en": "How many total sixes will be hit in the match?",
        "question_text_hi": "मैच में कुल कितने छक्के लगेंगे?",
        "category": QuestionCategory.MATCH,
        "options": [
            {"key": "A", "text_en": "0-8", "text_hi": "0-8", "max_value": 8},
            {"key": "B", "text_en": "9-14", "text_hi": "9-14", "min_value": 9, "max_value": 14},
            {"key": "C", "text_en": "15-20", "text_hi": "15-20", "min_value": 15, "max_value": 20},
            {"key": "D", "text_en": "21 or more", "text_hi": "21 या अधिक", "min_value": 21},
        ],
        "points": 60,
        "multiplier": 1.0,
        "evaluation_rules": {
            "type": EvaluationType.RANGE_MATCH,
            "metric": "total_sixes",
            "resolution_trigger": "match_end"
        },
        "difficulty": QuestionDifficulty.EASY
    },
    {
        "question_text_en": "How many total fours will be hit in the match?",
        "question_text_hi": "मैच में कुल कितने चौके लगेंगे?",
        "category": QuestionCategory.MATCH,
        "options": [
            {"key": "A", "text_en": "Less than 20", "text_hi": "20 से कम", "max_value": 19},
            {"key": "B", "text_en": "20-28", "text_hi": "20-28", "min_value": 20, "max_value": 28},
            {"key": "C", "text_en": "29-36", "text_hi": "29-36", "min_value": 29, "max_value": 36},
            {"key": "D", "text_en": "37 or more", "text_hi": "37 या अधिक", "min_value": 37},
        ],
        "points": 60,
        "multiplier": 1.0,
        "evaluation_rules": {
            "type": EvaluationType.RANGE_MATCH,
            "metric": "total_fours",
            "resolution_trigger": "match_end"
        },
        "difficulty": QuestionDifficulty.EASY
    },
    
    # Death Overs Questions
    {
        "question_text_en": "How many runs will be scored in death overs (16-20)?",
        "question_text_hi": "डेथ ओवर्स (16-20) में कितने रन बनेंगे?",
        "category": QuestionCategory.DEATH_OVERS,
        "options": [
            {"key": "A", "text_en": "Less than 50", "text_hi": "50 से कम", "max_value": 49},
            {"key": "B", "text_en": "50-65", "text_hi": "50-65", "min_value": 50, "max_value": 65},
            {"key": "C", "text_en": "66-80", "text_hi": "66-80", "min_value": 66, "max_value": 80},
            {"key": "D", "text_en": "More than 80", "text_hi": "80 से ज्यादा", "min_value": 81},
        ],
        "points": 70,
        "multiplier": 1.0,
        "evaluation_rules": {
            "type": EvaluationType.RANGE_MATCH,
            "metric": "death_overs_runs",
            "resolution_trigger": "innings_end"
        },
        "difficulty": QuestionDifficulty.MEDIUM
    },
    {
        "question_text_en": "How many wickets will fall in death overs (16-20)?",
        "question_text_hi": "डेथ ओवर्स (16-20) में कितने विकेट गिरेंगे?",
        "category": QuestionCategory.DEATH_OVERS,
        "options": [
            {"key": "A", "text_en": "0-1", "text_hi": "0-1", "max_value": 1},
            {"key": "B", "text_en": "2-3", "text_hi": "2-3", "min_value": 2, "max_value": 3},
            {"key": "C", "text_en": "4-5", "text_hi": "4-5", "min_value": 4, "max_value": 5},
            {"key": "D", "text_en": "6 or more", "text_hi": "6 या अधिक", "min_value": 6},
        ],
        "points": 75,
        "multiplier": 1.5,
        "evaluation_rules": {
            "type": EvaluationType.RANGE_MATCH,
            "metric": "death_overs_wickets",
            "resolution_trigger": "innings_end"
        },
        "difficulty": QuestionDifficulty.HARD
    },
]


# ==================== SAMPLE TEAMS ====================

SAMPLE_TEAMS = [
    {"name": "Mumbai Indians", "short_name": "MI", "color": "blue"},
    {"name": "Chennai Super Kings", "short_name": "CSK", "color": "yellow"},
    {"name": "Royal Challengers Bangalore", "short_name": "RCB", "color": "red"},
    {"name": "Kolkata Knight Riders", "short_name": "KKR", "color": "purple"},
    {"name": "Delhi Capitals", "short_name": "DC", "color": "blue"},
    {"name": "Punjab Kings", "short_name": "PBKS", "color": "red"},
    {"name": "Rajasthan Royals", "short_name": "RR", "color": "pink"},
    {"name": "Sunrisers Hyderabad", "short_name": "SRH", "color": "orange"},
    {"name": "Gujarat Titans", "short_name": "GT", "color": "teal"},
    {"name": "Lucknow Super Giants", "short_name": "LSG", "color": "teal"},
]

VENUES = [
    "Wankhede Stadium, Mumbai",
    "M. A. Chidambaram Stadium, Chennai",
    "M. Chinnaswamy Stadium, Bangalore",
    "Eden Gardens, Kolkata",
    "Arun Jaitley Stadium, Delhi",
    "Narendra Modi Stadium, Ahmedabad",
]


async def seed_database():
    """Main seeding function."""
    print("🌱 Starting database seeding...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.DB_NAME]
    
    # Check if data already exists (idempotent seeding)
    existing_questions = await db.questions.count_documents({})
    if existing_questions > 0:
        print("📝 Data already exists. Checking for missing seed data...")
        existing_matches = await db.matches.count_documents({})
        existing_templates = await db.templates.count_documents({})
        existing_contests = await db.contests.count_documents({})
        print(f"   Questions: {existing_questions}, Templates: {existing_templates}, Matches: {existing_matches}, Contests: {existing_contests}")
        
        if existing_questions >= 11 and existing_templates >= 1 and existing_matches >= 3 and existing_contests >= 3:
            print("✅ Seed data already complete. Skipping. Use --force flag to re-seed.")
            
            import sys as _sys
            if "--force" not in _sys.argv:
                client.close()
                return
        
        # Force re-seed: clear and re-insert
        print("🔄 Force re-seeding (--force flag or incomplete data)...")
        await db.questions.delete_many({})
        await db.templates.delete_many({})
        await db.matches.delete_many({})
        await db.contests.delete_many({})
    else:
        print("📝 No existing data. Fresh seeding...")
    
    # Seed Questions
    print("❓ Seeding questions...")
    question_ids = []
    for q_data in SAMPLE_QUESTIONS:
        question = Question(
            question_text_en=q_data["question_text_en"],
            question_text_hi=q_data["question_text_hi"],
            category=q_data["category"],
            options=[QuestionOption(**opt) for opt in q_data["options"]],
            points=q_data["points"],
            multiplier=q_data["multiplier"],
            evaluation_rules=EvaluationRules(**q_data["evaluation_rules"]),
            difficulty=q_data["difficulty"]
        )
        doc = question.model_dump()
        for key, value in doc.items():
            if isinstance(value, datetime):
                doc[key] = value.isoformat()
            elif hasattr(value, 'value'):  # Enum
                doc[key] = value.value
        
        # Handle nested enums
        doc['category'] = doc['category'].value if hasattr(doc['category'], 'value') else doc['category']
        doc['difficulty'] = doc['difficulty'].value if hasattr(doc['difficulty'], 'value') else doc['difficulty']
        doc['evaluation_rules']['type'] = doc['evaluation_rules']['type'].value if hasattr(doc['evaluation_rules']['type'], 'value') else doc['evaluation_rules']['type']
        
        await db.questions.insert_one(doc)
        question_ids.append(question.id)
    
    print(f"   ✅ Created {len(question_ids)} questions")
    
    # Seed Templates (using first 11 questions)
    print("📋 Seeding templates...")
    if len(question_ids) >= 11:
        template = Template(
            name="Standard T20 Template",
            description="Default template for T20 matches with 11 balanced questions",
            match_type=MatchType.T20,
            question_ids=question_ids[:11],
            total_points=sum(SAMPLE_QUESTIONS[i]["points"] * SAMPLE_QUESTIONS[i]["multiplier"] for i in range(11))
        )
        doc = template.model_dump()
        for key, value in doc.items():
            if isinstance(value, datetime):
                doc[key] = value.isoformat()
            elif hasattr(value, 'value'):
                doc[key] = value.value
        doc['match_type'] = doc['match_type'].value if hasattr(doc['match_type'], 'value') else doc['match_type']
        
        await db.templates.insert_one(doc)
        template_id = template.id
        print(f"   ✅ Created template: {template.name}")
    
    # Seed Sample Matches
    print("🏏 Seeding matches...")
    now = datetime.now(timezone.utc)
    matches_created = []
    
    for i in range(3):
        team_a_idx = i * 2
        team_b_idx = i * 2 + 1
        
        match = Match(
            team_a=Team(
                name=SAMPLE_TEAMS[team_a_idx]["name"],
                short_name=SAMPLE_TEAMS[team_a_idx]["short_name"]
            ),
            team_b=Team(
                name=SAMPLE_TEAMS[team_b_idx]["name"],
                short_name=SAMPLE_TEAMS[team_b_idx]["short_name"]
            ),
            venue=VENUES[i % len(VENUES)],
            match_type=MatchType.T20,
            status=MatchStatus.UPCOMING,
            start_time=now + timedelta(hours=2 + i * 24),
            templates_assigned=[template_id] if 'template_id' in dir() else []
        )
        
        doc = match.model_dump()
        for key, value in doc.items():
            if isinstance(value, datetime):
                doc[key] = value.isoformat()
            elif hasattr(value, 'value'):
                doc[key] = value.value
        doc['match_type'] = doc['match_type'].value if hasattr(doc['match_type'], 'value') else doc['match_type']
        doc['status'] = doc['status'].value if hasattr(doc['status'], 'value') else doc['status']
        
        await db.matches.insert_one(doc)
        matches_created.append(match)
        print(f"   ✅ {match.team_a.short_name} vs {match.team_b.short_name} - {match.start_time.strftime('%Y-%m-%d %H:%M')} UTC")
    
    # Seed Contests for first match
    print("🏆 Seeding contests...")
    if matches_created:
        first_match = matches_created[0]
        
        contests = [
            {
                "name": "Free Contest",
                "entry_fee": 0,
                "prize_pool": 1000,
                "max_participants": 100,
                "prize_distribution": [
                    {"rank_start": 1, "rank_end": 1, "prize": 500},
                    {"rank_start": 2, "rank_end": 5, "prize": 100},
                    {"rank_start": 6, "rank_end": 10, "prize": 50},
                ]
            },
            {
                "name": "Mini Contest",
                "entry_fee": 100,
                "prize_pool": 5000,
                "max_participants": 50,
                "prize_distribution": [
                    {"rank_start": 1, "rank_end": 1, "prize": 2500},
                    {"rank_start": 2, "rank_end": 3, "prize": 750},
                    {"rank_start": 4, "rank_end": 10, "prize": 100},
                ]
            },
            {
                "name": "Mega Contest",
                "entry_fee": 500,
                "prize_pool": 25000,
                "max_participants": 100,
                "prize_distribution": [
                    {"rank_start": 1, "rank_end": 1, "prize": 10000},
                    {"rank_start": 2, "rank_end": 3, "prize": 3000},
                    {"rank_start": 4, "rank_end": 10, "prize": 500},
                    {"rank_start": 11, "rank_end": 20, "prize": 200},
                ]
            },
        ]
        
        for c_data in contests:
            contest = Contest(
                match_id=first_match.id,
                template_id=template_id if 'template_id' in dir() else "",
                name=c_data["name"],
                entry_fee=c_data["entry_fee"],
                prize_pool=c_data["prize_pool"],
                max_participants=c_data["max_participants"],
                prize_distribution=[PrizeDistribution(**pd) for pd in c_data["prize_distribution"]],
                status=ContestStatus.OPEN,
                lock_time=first_match.start_time - timedelta(minutes=15)
            )
            
            doc = contest.model_dump()
            for key, value in doc.items():
                if isinstance(value, datetime):
                    doc[key] = value.isoformat()
                elif hasattr(value, 'value'):
                    doc[key] = value.value
            doc['status'] = doc['status'].value if hasattr(doc['status'], 'value') else doc['status']
            
            await db.contests.insert_one(doc)
            print(f"   ✅ {contest.name} - Entry: {contest.entry_fee} coins, Pool: {contest.prize_pool} coins")
    
    # Close connection
    client.close()
    
    print("\n🎉 Database seeding complete!")
    print(f"   Questions: {len(question_ids)}")
    print("   Templates: 1")
    print(f"   Matches: {len(matches_created)}")
    print("   Contests: 3")


if __name__ == "__main__":
    asyncio.run(seed_database())
