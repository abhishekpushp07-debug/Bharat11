"""
Seed Questions Bank & Templates
Creates 50+ cricket prediction questions (Hindi + English) and 5 match templates.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings
from models.schemas import generate_id, utc_now


QUESTIONS = [
    # MATCH_OUTCOME (10)
    {"en": "Which team will win this match?", "hi": "इस मैच में कौन सी टीम जीतेगी?", "cat": "match_outcome", "diff": "easy", "pts": 10,
     "options": [{"key": "A", "text_en": "Team A", "text_hi": "टीम A"}, {"key": "B", "text_en": "Team B", "text_hi": "टीम B"}, {"key": "C", "text_en": "Tie/Super Over", "text_hi": "टाई/सुपर ओवर"}, {"key": "D", "text_en": "No Result", "text_hi": "कोई परिणाम नहीं"}]},
    {"en": "Will the chasing team win?", "hi": "क्या पीछा करने वाली टीम जीतेगी?", "cat": "match_outcome", "diff": "easy", "pts": 10,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},
    {"en": "Winning margin range?", "hi": "जीत का अंतर कितना होगा?", "cat": "match_outcome", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "1-10 runs/1 wicket", "text_hi": "1-10 रन/1 विकेट"}, {"key": "B", "text_en": "11-30 runs/2-4 wkts", "text_hi": "11-30 रन/2-4 विकेट"}, {"key": "C", "text_en": "31-50 runs/5-7 wkts", "text_hi": "31-50 रन/5-7 विकेट"}, {"key": "D", "text_en": "50+ runs/8+ wkts", "text_hi": "50+ रन/8+ विकेट"}]},
    {"en": "Will the match go to the last over?", "hi": "क्या मैच आखिरी ओवर तक जाएगा?", "cat": "match_outcome", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},
    {"en": "Will there be a super over?", "hi": "क्या सुपर ओवर होगा?", "cat": "match_outcome", "diff": "hard", "pts": 25,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},
    {"en": "Toss winning team will choose to?", "hi": "टॉस जीतने वाली टीम क्या चुनेगी?", "cat": "match_outcome", "diff": "easy", "pts": 10,
     "options": [{"key": "A", "text_en": "Bat", "text_hi": "बैटिंग"}, {"key": "B", "text_en": "Bowl", "text_hi": "बॉलिंग"}]},
    {"en": "Who will win the toss?", "hi": "टॉस कौन जीतेगा?", "cat": "match_outcome", "diff": "easy", "pts": 5,
     "options": [{"key": "A", "text_en": "Team A", "text_hi": "टीम A"}, {"key": "B", "text_en": "Team B", "text_hi": "टीम B"}]},
    {"en": "Will DLS be applied?", "hi": "क्या DLS लागू होगा?", "cat": "match_outcome", "diff": "hard", "pts": 20,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},
    {"en": "Man of the Match will be from?", "hi": "मैन ऑफ द मैच किस टीम से होगा?", "cat": "match_outcome", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "Team A", "text_hi": "टीम A"}, {"key": "B", "text_en": "Team B", "text_hi": "टीम B"}]},
    {"en": "Will the defending total be achieved within 15 overs?", "hi": "क्या लक्ष्य 15 ओवर में हासिल होगा?", "cat": "match_outcome", "diff": "hard", "pts": 20,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},

    # RUNS (10)
    {"en": "Total runs in the first innings?", "hi": "पहली पारी में कुल कितने रन बनेंगे?", "cat": "runs", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "Less than 150", "text_hi": "150 से कम"}, {"key": "B", "text_en": "150-170", "text_hi": "150-170"}, {"key": "C", "text_en": "171-190", "text_hi": "171-190"}, {"key": "D", "text_en": "More than 190", "text_hi": "190 से ज़्यादा"}]},
    {"en": "Total runs scored in the match?", "hi": "मैच में कुल कितने रन बनेंगे?", "cat": "runs", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "Less than 300", "text_hi": "300 से कम"}, {"key": "B", "text_en": "300-340", "text_hi": "300-340"}, {"key": "C", "text_en": "341-380", "text_hi": "341-380"}, {"key": "D", "text_en": "More than 380", "text_hi": "380 से ज़्यादा"}]},
    {"en": "Powerplay runs (first 6 overs) for batting first team?", "hi": "पहले बल्लेबाज़ी करने वाली टीम के पॉवरप्ले रन?", "cat": "runs", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "Less than 40", "text_hi": "40 से कम"}, {"key": "B", "text_en": "40-55", "text_hi": "40-55"}, {"key": "C", "text_en": "56-70", "text_hi": "56-70"}, {"key": "D", "text_en": "More than 70", "text_hi": "70 से ज़्यादा"}]},
    {"en": "Runs in death overs (16-20)?", "hi": "डेथ ओवर (16-20) में कितने रन बनेंगे?", "cat": "runs", "diff": "hard", "pts": 20,
     "options": [{"key": "A", "text_en": "Less than 50", "text_hi": "50 से कम"}, {"key": "B", "text_en": "50-70", "text_hi": "50-70"}, {"key": "C", "text_en": "71-90", "text_hi": "71-90"}, {"key": "D", "text_en": "More than 90", "text_hi": "90 से ज़्यादा"}]},
    {"en": "Will any team score 200+?", "hi": "क्या कोई टीम 200+ रन बनाएगी?", "cat": "runs", "diff": "hard", "pts": 20,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},
    {"en": "Highest individual score range?", "hi": "सर्वोच्च व्यक्तिगत स्कोर कितना होगा?", "cat": "runs", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "Less than 40", "text_hi": "40 से कम"}, {"key": "B", "text_en": "40-60", "text_hi": "40-60"}, {"key": "C", "text_en": "61-80", "text_hi": "61-80"}, {"key": "D", "text_en": "80+", "text_hi": "80+"}]},
    {"en": "Will any batsman score a century?", "hi": "क्या कोई बल्लेबाज़ शतक लगाएगा?", "cat": "runs", "diff": "hard", "pts": 25,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},
    {"en": "Will any batsman score a fifty?", "hi": "क्या कोई बल्लेबाज़ अर्धशतक लगाएगा?", "cat": "runs", "diff": "easy", "pts": 10,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},
    {"en": "Runs scored in the first over?", "hi": "पहले ओवर में कितने रन बनेंगे?", "cat": "runs", "diff": "hard", "pts": 20,
     "options": [{"key": "A", "text_en": "0-4", "text_hi": "0-4"}, {"key": "B", "text_en": "5-8", "text_hi": "5-8"}, {"key": "C", "text_en": "9-12", "text_hi": "9-12"}, {"key": "D", "text_en": "13+", "text_hi": "13+"}]},
    {"en": "Middle overs (7-15) run rate?", "hi": "मिडिल ओवर (7-15) का रन रेट?", "cat": "runs", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "Less than 7", "text_hi": "7 से कम"}, {"key": "B", "text_en": "7-8.5", "text_hi": "7-8.5"}, {"key": "C", "text_en": "8.6-10", "text_hi": "8.6-10"}, {"key": "D", "text_en": "More than 10", "text_hi": "10 से ज़्यादा"}]},

    # WICKETS (10)
    {"en": "Total wickets in the match?", "hi": "मैच में कुल कितने विकेट गिरेंगे?", "cat": "wickets", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "Less than 10", "text_hi": "10 से कम"}, {"key": "B", "text_en": "10-14", "text_hi": "10-14"}, {"key": "C", "text_en": "15-18", "text_hi": "15-18"}, {"key": "D", "text_en": "More than 18", "text_hi": "18 से ज़्यादा"}]},
    {"en": "Wickets in the powerplay (first 6 overs)?", "hi": "पॉवरप्ले में कितने विकेट गिरेंगे?", "cat": "wickets", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "0-1", "text_hi": "0-1"}, {"key": "B", "text_en": "2", "text_hi": "2"}, {"key": "C", "text_en": "3", "text_hi": "3"}, {"key": "D", "text_en": "4+", "text_hi": "4+"}]},
    {"en": "Will any bowler take a 3+ wicket haul?", "hi": "क्या कोई गेंदबाज़ 3+ विकेट लेगा?", "cat": "wickets", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},
    {"en": "Will any bowler take a 5-wicket haul?", "hi": "क्या कोई गेंदबाज़ पंच विकेट लेगा?", "cat": "wickets", "diff": "hard", "pts": 25,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},
    {"en": "First wicket to fall within?", "hi": "पहला विकेट कब गिरेगा?", "cat": "wickets", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "First 3 overs", "text_hi": "पहले 3 ओवर में"}, {"key": "B", "text_en": "4-6 overs", "text_hi": "4-6 ओवर में"}, {"key": "C", "text_en": "7-10 overs", "text_hi": "7-10 ओवर में"}, {"key": "D", "text_en": "After 10 overs", "text_hi": "10 ओवर के बाद"}]},
    {"en": "Will there be a hat-trick?", "hi": "क्या हैट-ट्रिक होगी?", "cat": "wickets", "diff": "hard", "pts": 30,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},
    {"en": "How will the first wicket fall?", "hi": "पहला विकेट कैसे गिरेगा?", "cat": "wickets", "diff": "hard", "pts": 20,
     "options": [{"key": "A", "text_en": "Bowled/LBW", "text_hi": "बोल्ड/LBW"}, {"key": "B", "text_en": "Caught", "text_hi": "कैच"}, {"key": "C", "text_en": "Run Out", "text_hi": "रन आउट"}, {"key": "D", "text_en": "Other", "text_hi": "अन्य"}]},
    {"en": "Will any team be all out?", "hi": "क्या कोई टीम ऑल आउट होगी?", "cat": "wickets", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},
    {"en": "Bowling team's best figures?", "hi": "गेंदबाज़ी टीम का बेस्ट प्रदर्शन?", "cat": "wickets", "diff": "hard", "pts": 20,
     "options": [{"key": "A", "text_en": "1 wicket or less", "text_hi": "1 या कम विकेट"}, {"key": "B", "text_en": "2 wickets", "text_hi": "2 विकेट"}, {"key": "C", "text_en": "3 wickets", "text_hi": "3 विकेट"}, {"key": "D", "text_en": "4+ wickets", "text_hi": "4+ विकेट"}]},
    {"en": "Death overs wickets (16-20)?", "hi": "डेथ ओवर (16-20) में कितने विकेट?", "cat": "wickets", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "0-1", "text_hi": "0-1"}, {"key": "B", "text_en": "2-3", "text_hi": "2-3"}, {"key": "C", "text_en": "4-5", "text_hi": "4-5"}, {"key": "D", "text_en": "6+", "text_hi": "6+"}]},

    # BOUNDARIES (10)
    {"en": "Total sixes in the match?", "hi": "मैच में कुल कितने छक्के लगेंगे?", "cat": "boundaries", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "0-8", "text_hi": "0-8"}, {"key": "B", "text_en": "9-14", "text_hi": "9-14"}, {"key": "C", "text_en": "15-20", "text_hi": "15-20"}, {"key": "D", "text_en": "21+", "text_hi": "21+"}]},
    {"en": "Total fours in the match?", "hi": "मैच में कुल कितने चौके लगेंगे?", "cat": "boundaries", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "Less than 20", "text_hi": "20 से कम"}, {"key": "B", "text_en": "20-30", "text_hi": "20-30"}, {"key": "C", "text_en": "31-40", "text_hi": "31-40"}, {"key": "D", "text_en": "More than 40", "text_hi": "40 से ज़्यादा"}]},
    {"en": "Total boundaries (4s+6s) in powerplay?", "hi": "पॉवरप्ले में कुल बाउंड्री (4+6)?", "cat": "boundaries", "diff": "hard", "pts": 20,
     "options": [{"key": "A", "text_en": "0-5", "text_hi": "0-5"}, {"key": "B", "text_en": "6-10", "text_hi": "6-10"}, {"key": "C", "text_en": "11-15", "text_hi": "11-15"}, {"key": "D", "text_en": "16+", "text_hi": "16+"}]},
    {"en": "Most sixes by a single player?", "hi": "एक खिलाड़ी के सबसे ज़्यादा छक्के?", "cat": "boundaries", "diff": "hard", "pts": 20,
     "options": [{"key": "A", "text_en": "0-2", "text_hi": "0-2"}, {"key": "B", "text_en": "3-4", "text_hi": "3-4"}, {"key": "C", "text_en": "5-6", "text_hi": "5-6"}, {"key": "D", "text_en": "7+", "text_hi": "7+"}]},
    {"en": "Will there be a six in the first over?", "hi": "क्या पहले ओवर में छक्का लगेगा?", "cat": "boundaries", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},
    {"en": "Which innings will have more sixes?", "hi": "किस पारी में ज़्यादा छक्के लगेंगे?", "cat": "boundaries", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "First Innings", "text_hi": "पहली पारी"}, {"key": "B", "text_en": "Second Innings", "text_hi": "दूसरी पारी"}, {"key": "C", "text_en": "Equal", "text_hi": "बराबर"}]},
    {"en": "Longest six in the match (meters)?", "hi": "मैच का सबसे लंबा छक्का (मीटर)?", "cat": "boundaries", "diff": "hard", "pts": 20,
     "options": [{"key": "A", "text_en": "Less than 80m", "text_hi": "80m से कम"}, {"key": "B", "text_en": "80-90m", "text_hi": "80-90m"}, {"key": "C", "text_en": "91-100m", "text_hi": "91-100m"}, {"key": "D", "text_en": "100m+", "text_hi": "100m+"}]},
    {"en": "Will the last ball of the match be a boundary?", "hi": "क्या मैच की आखिरी गेंद बाउंड्री होगी?", "cat": "boundaries", "diff": "hard", "pts": 25,
     "options": [{"key": "A", "text_en": "Yes (Four)", "text_hi": "हाँ (चौका)"}, {"key": "B", "text_en": "Yes (Six)", "text_hi": "हाँ (छक्का)"}, {"key": "C", "text_en": "No", "text_hi": "नहीं"}]},
    {"en": "Boundaries in death overs (16-20)?", "hi": "डेथ ओवर (16-20) में बाउंड्री?", "cat": "boundaries", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "0-5", "text_hi": "0-5"}, {"key": "B", "text_en": "6-10", "text_hi": "6-10"}, {"key": "C", "text_en": "11-15", "text_hi": "11-15"}, {"key": "D", "text_en": "16+", "text_hi": "16+"}]},
    {"en": "Total extras (wides+no-balls+byes)?", "hi": "कुल एक्स्ट्रा (वाइड+नो-बॉल+बाई)?", "cat": "boundaries", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "0-8", "text_hi": "0-8"}, {"key": "B", "text_en": "9-14", "text_hi": "9-14"}, {"key": "C", "text_en": "15-20", "text_hi": "15-20"}, {"key": "D", "text_en": "21+", "text_hi": "21+"}]},

    # PLAYER_PERFORMANCE (10)
    {"en": "Opening partnership runs?", "hi": "ओपनिंग जोड़ी कितने रन बनाएगी?", "cat": "player_performance", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "Less than 25", "text_hi": "25 से कम"}, {"key": "B", "text_en": "25-50", "text_hi": "25-50"}, {"key": "C", "text_en": "51-75", "text_hi": "51-75"}, {"key": "D", "text_en": "More than 75", "text_hi": "75 से ज़्यादा"}]},
    {"en": "Will there be a run out?", "hi": "क्या कोई रन आउट होगा?", "cat": "player_performance", "diff": "easy", "pts": 10,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},
    {"en": "Top scorer's strike rate?", "hi": "टॉप स्कोरर का स्ट्राइक रेट?", "cat": "player_performance", "diff": "hard", "pts": 20,
     "options": [{"key": "A", "text_en": "Less than 120", "text_hi": "120 से कम"}, {"key": "B", "text_en": "120-150", "text_hi": "120-150"}, {"key": "C", "text_en": "151-180", "text_hi": "151-180"}, {"key": "D", "text_en": "180+", "text_hi": "180+"}]},
    {"en": "Best bowling economy rate?", "hi": "सबसे अच्छी बॉलिंग इकॉनमी रेट?", "cat": "player_performance", "diff": "hard", "pts": 20,
     "options": [{"key": "A", "text_en": "Less than 6", "text_hi": "6 से कम"}, {"key": "B", "text_en": "6-8", "text_hi": "6-8"}, {"key": "C", "text_en": "8.1-10", "text_hi": "8.1-10"}, {"key": "D", "text_en": "More than 10", "text_hi": "10 से ज़्यादा"}]},
    {"en": "Will there be a maiden over?", "hi": "क्या कोई मेडन ओवर होगा?", "cat": "player_performance", "diff": "hard", "pts": 20,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},
    {"en": "Highest partnership in the match?", "hi": "मैच में सबसे बड़ी साझेदारी?", "cat": "player_performance", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "Less than 40", "text_hi": "40 से कम"}, {"key": "B", "text_en": "40-70", "text_hi": "40-70"}, {"key": "C", "text_en": "71-100", "text_hi": "71-100"}, {"key": "D", "text_en": "100+", "text_hi": "100+"}]},
    {"en": "Will a catch be dropped?", "hi": "क्या कोई कैच छूटेगा?", "cat": "player_performance", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},
    {"en": "Fastest fifty (balls)?", "hi": "सबसे तेज़ अर्धशतक (गेंदों में)?", "cat": "player_performance", "diff": "hard", "pts": 20,
     "options": [{"key": "A", "text_en": "Less than 20", "text_hi": "20 से कम"}, {"key": "B", "text_en": "20-28", "text_hi": "20-28"}, {"key": "C", "text_en": "29-35", "text_hi": "29-35"}, {"key": "D", "text_en": "35+ or no fifty", "text_hi": "35+ या कोई अर्धशतक नहीं"}]},
    {"en": "Number of dot balls in the match?", "hi": "मैच में कुल डॉट बॉल?", "cat": "player_performance", "diff": "hard", "pts": 20,
     "options": [{"key": "A", "text_en": "Less than 60", "text_hi": "60 से कम"}, {"key": "B", "text_en": "60-80", "text_hi": "60-80"}, {"key": "C", "text_en": "81-100", "text_hi": "81-100"}, {"key": "D", "text_en": "100+", "text_hi": "100+"}]},
    {"en": "Will there be a stumping?", "hi": "क्या कोई स्टम्पिंग होगी?", "cat": "player_performance", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},

    # MILESTONE (5)
    {"en": "Number of 50+ scores in the match?", "hi": "मैच में 50+ स्कोर कितने होंगे?", "cat": "milestone", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "0", "text_hi": "0"}, {"key": "B", "text_en": "1-2", "text_hi": "1-2"}, {"key": "C", "text_en": "3-4", "text_hi": "3-4"}, {"key": "D", "text_en": "5+", "text_hi": "5+"}]},
    {"en": "Highest score in the match?", "hi": "मैच का सर्वोच्च स्कोर?", "cat": "milestone", "diff": "hard", "pts": 20,
     "options": [{"key": "A", "text_en": "Below 50", "text_hi": "50 से कम"}, {"key": "B", "text_en": "50-75", "text_hi": "50-75"}, {"key": "C", "text_en": "76-100", "text_hi": "76-100"}, {"key": "D", "text_en": "100+", "text_hi": "100+"}]},
    {"en": "Most wickets by one bowler?", "hi": "एक गेंदबाज़ के सबसे ज़्यादा विकेट?", "cat": "milestone", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "0-1", "text_hi": "0-1"}, {"key": "B", "text_en": "2", "text_hi": "2"}, {"key": "C", "text_en": "3", "text_hi": "3"}, {"key": "D", "text_en": "4+", "text_hi": "4+"}]},
    {"en": "Will any player hit 5+ sixes?", "hi": "क्या कोई खिलाड़ी 5+ छक्के मारेगा?", "cat": "milestone", "diff": "hard", "pts": 25,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},
    {"en": "Total number of extras in the match?", "hi": "मैच में कुल एक्स्ट्रा?", "cat": "milestone", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "0-10", "text_hi": "0-10"}, {"key": "B", "text_en": "11-18", "text_hi": "11-18"}, {"key": "C", "text_en": "19-25", "text_hi": "19-25"}, {"key": "D", "text_en": "25+", "text_hi": "25+"}]},

    # SPECIAL (5)
    {"en": "Will there be a DRS review?", "hi": "क्या DRS रिव्यू होगा?", "cat": "special", "diff": "easy", "pts": 10,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},
    {"en": "Successful DRS reviews in the match?", "hi": "मैच में सफल DRS रिव्यू?", "cat": "special", "diff": "hard", "pts": 20,
     "options": [{"key": "A", "text_en": "0", "text_hi": "0"}, {"key": "B", "text_en": "1", "text_hi": "1"}, {"key": "C", "text_en": "2", "text_hi": "2"}, {"key": "D", "text_en": "3+", "text_hi": "3+"}]},
    {"en": "Will there be a no-ball followed by a free hit boundary?", "hi": "क्या नो-बॉल के बाद फ्री हिट पर बाउंड्री आएगी?", "cat": "special", "diff": "hard", "pts": 25,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},
    {"en": "Strategic timeout score after 10 overs?", "hi": "10 ओवर बाद स्ट्रैटेजिक टाइमआउट स्कोर?", "cat": "special", "diff": "medium", "pts": 15,
     "options": [{"key": "A", "text_en": "Less than 70", "text_hi": "70 से कम"}, {"key": "B", "text_en": "70-85", "text_hi": "70-85"}, {"key": "C", "text_en": "86-100", "text_hi": "86-100"}, {"key": "D", "text_en": "100+", "text_hi": "100+"}]},
    {"en": "Will there be a rain interruption?", "hi": "क्या बारिश से रुकावट आएगी?", "cat": "special", "diff": "hard", "pts": 20,
     "options": [{"key": "A", "text_en": "Yes", "text_hi": "हाँ"}, {"key": "B", "text_en": "No", "text_hi": "नहीं"}]},
]


TEMPLATES = [
    {"name": "T20 Standard - Match Basics", "desc": "Basic prediction template for T20 matches covering outcome, runs and wickets", "type": "T20", "q_indices": [0, 1, 5, 10, 11, 12, 20, 21, 30, 40, 50]},
    {"name": "T20 Aggressive - Boundary Heavy", "desc": "Focus on boundaries, sixes and high-scoring predictions", "type": "T20", "q_indices": [0, 10, 13, 14, 30, 31, 32, 33, 34, 35, 16]},
    {"name": "T20 Strategic - Death Overs", "desc": "Focus on death overs, powerplay and strategic moments", "type": "T20", "q_indices": [3, 12, 13, 19, 22, 29, 38, 4, 43, 44, 2]},
    {"name": "T20 All-Rounder - Mixed", "desc": "Balanced mix of all categories for a complete prediction experience", "type": "T20", "q_indices": [0, 1, 10, 15, 20, 23, 30, 33, 40, 43, 45]},
    {"name": "T20 Expert - High Risk", "desc": "Difficult questions with high points for experienced predictors", "type": "T20", "q_indices": [4, 7, 14, 16, 18, 23, 25, 27, 36, 37, 42]},
]


async def seed_questions():
    """Seed 50+ questions and 5 templates."""
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.DB_NAME]

    # Check existing questions
    existing = await db.questions.count_documents({})
    if existing >= 50:
        print(f"Questions already seeded ({existing} found). Use --force to re-seed.")
        if "--force" not in sys.argv:
            client.close()
            return
        print("Force re-seeding questions and templates...")
        await db.questions.delete_many({})
        await db.templates.delete_many({})

    now = utc_now().isoformat()
    question_docs = []
    question_ids = []

    for q in QUESTIONS:
        qid = generate_id()
        question_ids.append(qid)
        doc = {
            "id": qid,
            "question_text_en": q["en"],
            "question_text_hi": q["hi"],
            "category": q["cat"],
            "difficulty": q["diff"],
            "options": q["options"],
            "points": q["pts"],
            "evaluation_rules": {
                "type": "exact_match",
                "source_field": "",
                "condition": "",
                "threshold": 0,
                "bonus_multiplier": 1.0
            },
            "correct_option": None,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
        question_docs.append(doc)

    await db.questions.insert_many(question_docs)
    print(f"Seeded {len(question_docs)} questions")

    # Create templates
    template_docs = []
    for t in TEMPLATES:
        # Resolve question indices to IDs (capped at available)
        t_qids = [question_ids[i] for i in t["q_indices"] if i < len(question_ids)]
        total_pts = sum(question_docs[i]["points"] for i in t["q_indices"] if i < len(question_docs))
        
        doc = {
            "id": generate_id(),
            "name": t["name"],
            "description": t["desc"],
            "match_type": t["type"],
            "question_ids": t_qids,
            "total_points": total_pts,
            "question_count": len(t_qids),
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
        template_docs.append(doc)

    await db.templates.insert_many(template_docs)
    print(f"Seeded {len(template_docs)} templates")

    # Print summary
    cats = {}
    for q in question_docs:
        cat = q["category"]
        cats[cat] = cats.get(cat, 0) + 1
    print("Questions by category:")
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")

    client.close()
    print("Done!")


if __name__ == "__main__":
    asyncio.run(seed_questions())
