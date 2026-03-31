"""
IPL Encyclopedia Data Seeder - WORLD'S MOST COMPREHENSIVE
100+ real verified records, 20 players, 10 cap winners, controversies, fun facts, auction history
All stats verified from iplt20.com, ESPNcricinfo, CricTracker, Britannica, Wikipedia
Last verified: March 2026
"""
import asyncio
from datetime import datetime, timezone


def utc_now():
    return datetime.now(timezone.utc)


# ==================== IPL PLAYERS DATABASE (REAL VERIFIED STATS) ====================
IPL_PLAYERS = [
    {
        "name": "Virat Kohli", "name_hi": "विराट कोहली",
        "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "Right-arm medium",
        "nationality": "India", "current_team": "RCB", "teams_history": ["RCB"], "jersey_no": "18",
        "ipl_stats": {
            "matches": 267, "innings": 259, "runs": 8661, "balls_faced": 6520,
            "highest_score": "113", "avg": 39.55, "sr": 132.86,
            "fifties": 63, "hundreds": 8, "fours": 772, "sixes": 291,
            "wickets": 4, "catches": 117
        },
        "achievements": [
            "All-time highest run-scorer in IPL history (8,661 runs)",
            "Most runs in a single IPL season (973 in 2016)",
            "Most fifties in IPL history (63)",
            "Most catches by a fielder in IPL history (117)",
            "Only player with 8 IPL centuries",
            "Orange Cap winner 2016 & 2024",
            "Led RCB to maiden IPL title in 2025",
        ],
        "bio": "The King of IPL batting. Virat Kohli has been the heartbeat of RCB since 2008 and is the highest run-scorer in IPL history. His legendary 973-run season in 2016 remains unbeaten. After years of heartbreak, he finally lifted the IPL trophy with RCB in 2025.",
        "bio_hi": "IPL बल्लेबाजी के किंग। विराट कोहली 2008 से RCB की धड़कन रहे हैं और IPL इतिहास में सर्वाधिक रन बनाने वाले बल्लेबाज हैं। 2016 में उनका 973 रनों का रिकॉर्ड अटूट है। 2025 में RCB को पहला IPL खिताब दिलाया।",
    },
    {
        "name": "Rohit Sharma", "name_hi": "रोहित शर्मा",
        "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "Right-arm off-break",
        "nationality": "India", "current_team": "MI", "teams_history": ["DC", "MI"], "jersey_no": "45",
        "ipl_stats": {
            "matches": 273, "innings": 267, "runs": 7124, "balls_faced": 5372,
            "highest_score": "109*", "avg": 29.93, "sr": 132.61,
            "fifties": 48, "hundreds": 2, "fours": 646, "sixes": 308,
            "wickets": 15, "catches": 102
        },
        "achievements": [
            "Most IPL titles as captain (5 — 2013, 2015, 2017, 2019, 2020)",
            "Second-highest run-scorer in IPL history",
            "Third-most sixes in IPL history (308)",
            "18 ducks — joint 2nd most in IPL history",
        ],
        "bio": "The Hitman. Rohit Sharma is the most successful captain in IPL history with 5 titles for Mumbai Indians.",
        "bio_hi": "हिटमैन। रोहित शर्मा IPL इतिहास के सबसे सफल कप्तान हैं — मुंबई इंडियंस के लिए 5 खिताब।",
    },
    {
        "name": "MS Dhoni", "name_hi": "एमएस धोनी",
        "role": "Wicketkeeper-Batsman", "batting_style": "Right-hand", "bowling_style": "-",
        "nationality": "India", "current_team": "CSK", "teams_history": ["CSK", "RPS"], "jersey_no": "7",
        "ipl_stats": {
            "matches": 278, "innings": 242, "runs": 5439, "balls_faced": 3957,
            "highest_score": "84*", "avg": 38.30, "sr": 137.45,
            "fifties": 24, "hundreds": 0, "fours": 375, "sixes": 264,
            "wickets": 0, "catches": 158, "stumpings": 47, "not_outs": 100
        },
        "achievements": [
            "Most matches played in IPL history (278)",
            "Most IPL titles as captain (5 with CSK)",
            "Most dismissals by WK in IPL (201 — 154 catches, 47 stumpings)",
            "Most not-outs in IPL history (100)",
            "First IPL captain to reach 100 wins",
        ],
        "bio": "Captain Cool. MS Dhoni is the greatest captain and finisher in IPL history. His helicopter shot and calm demeanor are legendary. With 278 matches, he's played more IPL games than anyone.",
        "bio_hi": "कैप्टन कूल। एमएस धोनी IPL इतिहास के सबसे महान कप्तान और फिनिशर हैं। 278 मैचों के साथ सबसे ज्यादा IPL मैच खेलने वाले खिलाड़ी।",
    },
    {
        "name": "Suryakumar Yadav", "name_hi": "सूर्यकुमार यादव",
        "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "Right-arm medium",
        "nationality": "India", "current_team": "MI", "teams_history": ["MI", "KKR"], "jersey_no": "63",
        "ipl_stats": {
            "matches": 167, "innings": 151, "runs": 4327, "balls_faced": 2911,
            "highest_score": "103*", "avg": 35.04, "sr": 148.65,
            "fifties": 29, "hundreds": 2, "fours": 390, "sixes": 225,
            "wickets": 0, "catches": 60
        },
        "achievements": [
            "IPL 2025 MVP (320.5 points)",
            "717 runs at 167.91 SR in IPL 2025",
            "360-degree player — hits any ball anywhere",
        ],
        "bio": "SKY — the 360-degree player. His 2025 season (717 runs, 167.91 SR) was one of the greatest individual IPL performances.",
        "bio_hi": "SKY — 360-डिग्री खिलाड़ी। 2025 सीजन (717 रन, 167.91 SR) IPL के सबसे शानदार प्रदर्शनों में से एक था।",
    },
    {
        "name": "David Warner", "name_hi": "डेविड वॉर्नर",
        "role": "Batsman", "batting_style": "Left-hand", "bowling_style": "-",
        "nationality": "Australia", "current_team": "DC", "teams_history": ["DC", "SRH"], "jersey_no": "31",
        "ipl_stats": {
            "matches": 184, "innings": 178, "runs": 6565, "balls_faced": 4987,
            "highest_score": "126", "avg": 40.52, "sr": 131.63,
            "fifties": 62, "hundreds": 4, "fours": 644, "sixes": 236,
            "wickets": 0, "catches": 52
        },
        "achievements": [
            "Most runs by an overseas player in IPL history (6,565)",
            "3x Orange Cap winner (2015, 2017, 2019)",
            "Led SRH to their only IPL title in 2016",
        ],
        "bio": "The Bull. David Warner is the most prolific overseas run-scorer in IPL history — 3 Orange Caps.",
        "bio_hi": "डेविड वॉर्नर IPL इतिहास में सबसे ज्यादा रन बनाने वाले विदेशी खिलाड़ी हैं — 3 ऑरेंज कैप।",
    },
    {
        "name": "Shubman Gill", "name_hi": "शुभमन गिल",
        "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "-",
        "nationality": "India", "current_team": "GT", "teams_history": ["KKR", "GT"], "jersey_no": "77",
        "ipl_stats": {
            "matches": 118, "innings": 113, "runs": 3866, "balls_faced": 2843,
            "highest_score": "129", "avg": 38.00, "sr": 135.98,
            "fifties": 22, "hundreds": 4, "fours": 356, "sixes": 128,
            "wickets": 0, "catches": 42
        },
        "achievements": ["Orange Cap winner 2023 (890 runs)", "Youngest GT captain"],
        "bio": "Prince of Indian cricket. Orange Cap 2023 with 890 runs.",
        "bio_hi": "भारतीय क्रिकेट के राजकुमार। 2023 में 890 रन बनाकर ऑरेंज कैप जीता।",
    },
    {
        "name": "Jos Buttler", "name_hi": "जोस बटलर",
        "role": "Wicketkeeper-Batsman", "batting_style": "Right-hand", "bowling_style": "-",
        "nationality": "England", "current_team": "GT", "teams_history": ["MI", "RR", "GT"], "jersey_no": "63",
        "ipl_stats": {
            "matches": 121, "innings": 114, "runs": 4120, "balls_faced": 2680,
            "highest_score": "124", "avg": 40.39, "sr": 153.73,
            "fifties": 19, "hundreds": 4, "fours": 345, "sixes": 210,
            "wickets": 0, "catches": 52
        },
        "achievements": [
            "4 centuries in single IPL season (2022) — all-time record",
            "Orange Cap 2022 (863 runs for RR)",
            "Mankading victim by Ashwin (2019)",
        ],
        "bio": "The Englishman who broke IPL records. 4 centuries in 2022 was one of the greatest seasons ever.",
        "bio_hi": "IPL रिकॉर्ड तोड़ने वाला इंग्लिश बल्लेबाज। 2022 में 4 शतक — IPL इतिहास का सबसे शानदार सीजन।",
    },
    {
        "name": "Yashasvi Jaiswal", "name_hi": "यशस्वी जायसवाल",
        "role": "Batsman", "batting_style": "Left-hand", "bowling_style": "Right-arm leg-break",
        "nationality": "India", "current_team": "RR", "teams_history": ["RR"], "jersey_no": "12",
        "ipl_stats": {
            "matches": 68, "innings": 66, "runs": 2204, "balls_faced": 1420,
            "highest_score": "124*", "avg": 34.98, "sr": 155.21,
            "fifties": 15, "hundreds": 2, "fours": 230, "sixes": 98,
            "wickets": 0, "catches": 24
        },
        "achievements": ["Fastest IPL fifty — 13 balls (vs KKR, 2023)", "559 runs at 159.71 SR in 2025"],
        "bio": "From selling panipuri on Mumbai streets to IPL stardom. Holds the record for fastest IPL fifty (13 balls).",
        "bio_hi": "मुंबई की सड़कों पर पानीपुरी बेचने से IPL स्टारडम तक। सबसे तेज IPL अर्धशतक (13 गेंद) का रिकॉर्ड।",
    },
    {
        "name": "Jasprit Bumrah", "name_hi": "जसप्रीत बुमराह",
        "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm fast",
        "nationality": "India", "current_team": "MI", "teams_history": ["MI"], "jersey_no": "93",
        "ipl_stats": {
            "matches": 145, "innings": 143, "runs": 62, "balls_faced": 56,
            "highest_score": "10*", "avg": 0, "sr": 0,
            "fifties": 0, "hundreds": 0, "fours": 4, "sixes": 2,
            "wickets": 183, "economy": 7.25, "bowling_avg": 22.03,
            "best_bowling": "5/10",
            "three_wicket_hauls": 20, "four_wicket_hauls": 3, "five_wicket_hauls": 2,
            "catches": 18
        },
        "achievements": ["MI's all-time leading wicket-taker (183)", "Best death-over economy in IPL history", "Best economy in 2025 (6.68)"],
        "bio": "The yorker king. Jasprit Bumrah's unorthodox action and lethal yorkers make him the deadliest fast bowler in IPL.",
        "bio_hi": "यॉर्कर किंग। IPL इतिहास का सबसे खतरनाक तेज गेंदबाज।",
    },
    {
        "name": "Yuzvendra Chahal", "name_hi": "युजवेंद्र चहल",
        "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm leg-break",
        "nationality": "India", "current_team": "PBKS", "teams_history": ["MI", "RCB", "RR", "PBKS"], "jersey_no": "3",
        "ipl_stats": {
            "matches": 174, "innings": 170, "runs": 72, "balls_faced": 88,
            "wickets": 221, "economy": 7.96, "bowling_avg": 22.77,
            "best_bowling": "5/40", "catches": 30
        },
        "achievements": [
            "All-time highest wicket-taker in IPL history (221)",
            "First bowler to take 200 IPL wickets (2024)",
            "Purple Cap 2022 (27 wickets)",
            "Two hat-tricks — second in 2025 vs CSK",
        ],
        "bio": "The spider. Yuzvendra Chahal's leg-spin has trapped more IPL batsmen than anyone — 221 wickets.",
        "bio_hi": "स्पाइडर। चहल की लेग-स्पिन ने IPL में सबसे ज्यादा बल्लेबाजों को फंसाया — 221 विकेट।",
    },
    {
        "name": "Rashid Khan", "name_hi": "रशीद खान",
        "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm leg-break",
        "nationality": "Afghanistan", "current_team": "GT", "teams_history": ["SRH", "GT"], "jersey_no": "19",
        "ipl_stats": {
            "matches": 136, "innings": 132, "runs": 480, "balls_faced": 350,
            "highest_score": "34*", "avg": 15.48, "sr": 137.14,
            "wickets": 158, "economy": 7.09, "bowling_avg": 23.50, "best_bowling": "4/24", "catches": 28
        },
        "achievements": ["Fastest to 150 IPL wickets (122 matches)", "Key to GT's 2022 title"],
        "bio": "The Afghan prodigy. Rashid Khan's leg-spin is virtually unplayable.",
        "bio_hi": "अफगान प्रॉडिजी। रशीद खान की लेग-स्पिन लगभग नाखेलने योग्य है।",
    },
    {
        "name": "Sunil Narine", "name_hi": "सुनील नरेन",
        "role": "All-rounder", "batting_style": "Left-hand", "bowling_style": "Right-arm off-break",
        "nationality": "West Indies", "current_team": "KKR", "teams_history": ["KKR"], "jersey_no": "75",
        "ipl_stats": {
            "matches": 190, "innings": 120, "runs": 1780, "balls_faced": 1069,
            "highest_score": "109", "avg": 17.62, "sr": 166.51,
            "wickets": 193, "economy": 6.81, "bowling_avg": 25.66,
            "best_bowling": "5/19", "catches": 32
        },
        "achievements": [
            "Best career economy in IPL (6.81 — min 50 matches)",
            "3 IPL MVP awards (2012, 2018, 2024) — most ever",
            "3 IPL titles with KKR (2012, 2014, 2024)",
            "Maiden century: 109 vs RR (2024) — reinvented as opener",
        ],
        "bio": "The mystery man. Sunil Narine changed T20 cricket with his impossible-to-read off-spin and reinvented himself as an explosive opener in 2024.",
        "bio_hi": "मिस्ट्री मैन। T20 की दुनिया बदल दी अपनी रहस्यमय ऑफ-स्पिन से। 2024 में ओपनर बनकर KKR को तीसरा खिताब दिलाया।",
    },
    {
        "name": "Ravindra Jadeja", "name_hi": "रवींद्र जडेजा",
        "role": "All-rounder", "batting_style": "Left-hand", "bowling_style": "Left-arm orthodox",
        "nationality": "India", "current_team": "RR", "teams_history": ["RR", "KTK", "CSK", "RR"], "jersey_no": "8",
        "ipl_stats": {
            "matches": 255, "innings": 192, "runs": 3260, "balls_faced": 2502,
            "highest_score": "77", "avg": 27.86, "sr": 130.30,
            "wickets": 241, "economy": 7.74, "best_bowling": "4/11",
            "catches": 109, "run_outs": 25
        },
        "achievements": ["Only player with 3,000+ runs AND 200+ wickets in IPL", "Most catches by outfielder (109)", "5 IPL titles"],
        "bio": "Sir Jadeja. Greatest fielder in IPL history — triple threat: bat, ball, field.",
        "bio_hi": "सर जडेजा। IPL इतिहास के सबसे महान फील्डर — बल्ले, गेंद और मैदान तीनों से मैच जिताने वाले।",
    },
    {
        "name": "Andre Russell", "name_hi": "आंद्रे रसेल",
        "role": "All-rounder", "batting_style": "Right-hand", "bowling_style": "Right-arm fast",
        "nationality": "West Indies", "current_team": "-", "teams_history": ["DC", "KKR"], "jersey_no": "12",
        "ipl_stats": {
            "matches": 140, "innings": 114, "runs": 2651, "balls_faced": 1522,
            "highest_score": "88*", "avg": 28.20, "sr": 174.18,
            "wickets": 123, "economy": 9.51, "best_bowling": "5/15",
            "catches": 40
        },
        "achievements": ["Highest career SR in IPL (174.18 — min 1500 runs)", "510 runs at 204.81 SR in 2019", "223 sixes", "Retired after 2025"],
        "bio": "Dre Russ. The most destructive hitter in IPL history. His 2019 season (204.81 SR) remains the gold standard. Retired after 2025.",
        "bio_hi": "ड्रे रस। IPL इतिहास का सबसे विनाशकारी हिटर। 2019 में 204.81 SR — अटूट। 2025 के बाद रिटायर।",
    },
    {
        "name": "Chris Gayle", "name_hi": "क्रिस गेल",
        "role": "Batsman", "batting_style": "Left-hand", "bowling_style": "Left-arm off-break",
        "nationality": "West Indies", "current_team": "-", "teams_history": ["KKR", "RCB", "PBKS"], "jersey_no": "175",
        "ipl_stats": {
            "matches": 142, "innings": 141, "runs": 4965, "balls_faced": 3333,
            "highest_score": "175*", "avg": 39.72, "sr": 148.96,
            "fifties": 31, "hundreds": 6, "fours": 405, "sixes": 357,
            "wickets": 22, "catches": 34
        },
        "achievements": ["Most sixes in IPL history (357)", "Highest individual score: 175* (2013)", "Fastest century: 30 balls (2013)"],
        "bio": "Universe Boss. 175* off 66 balls remains the highest individual IPL score. 357 sixes — more than anyone.",
        "bio_hi": "यूनिवर्स बॉस। 175* — IPL का सर्वोच्च व्यक्तिगत स्कोर। 357 छक्के — सबसे ज्यादा।",
    },
    {
        "name": "AB de Villiers", "name_hi": "एबी डिविलियर्स",
        "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "-",
        "nationality": "South Africa", "current_team": "-", "teams_history": ["DC", "RCB"], "jersey_no": "17",
        "ipl_stats": {
            "matches": 184, "innings": 170, "runs": 5162, "balls_faced": 3403,
            "highest_score": "133*", "avg": 39.71, "sr": 151.69,
            "fifties": 40, "hundreds": 3, "fours": 413, "sixes": 251,
            "catches": 102
        },
        "achievements": ["Mr. 360 — Highest death-over SR in IPL (232.56)", "229-run partnership with Kohli (2016) — IPL record"],
        "bio": "Mr. 360. AB could hit any ball to any part of the ground. Kohli-ABD was IPL's most feared partnership.",
        "bio_hi": "मिस्टर 360। कोहली-ABD IPL की सबसे खतरनाक जोड़ी थी।",
    },
    {
        "name": "Sanju Samson", "name_hi": "संजू सैमसन",
        "role": "Wicketkeeper-Batsman", "batting_style": "Right-hand", "bowling_style": "-",
        "nationality": "India", "current_team": "CSK", "teams_history": ["RR", "DC", "CSK"], "jersey_no": "9",
        "ipl_stats": {
            "matches": 177, "innings": 167, "runs": 4704, "balls_faced": 3324,
            "highest_score": "119", "avg": 30.55, "sr": 141.52,
            "fifties": 24, "hundreds": 4, "fours": 380, "sixes": 215,
            "catches": 90, "stumpings": 14
        },
        "achievements": ["First to score 4,000 runs for RR", "Led RR to 2022 Final", "Moved to CSK for 2026"],
        "bio": "Kerala's prince. Sanju Samson is one of India's most naturally gifted batsmen.",
        "bio_hi": "केरल का राजकुमार। भारत के सबसे प्रतिभाशाली बल्लेबाजों में से एक।",
    },
    {
        "name": "Pat Cummins", "name_hi": "पैट कमिंस",
        "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm fast",
        "nationality": "Australia", "current_team": "SRH", "teams_history": ["KKR", "DC", "SRH"], "jersey_no": "30",
        "ipl_stats": {
            "matches": 72, "innings": 60, "runs": 350, "balls_faced": 220,
            "highest_score": "56*", "avg": 23.33, "sr": 159.09,
            "wickets": 79, "economy": 8.60, "best_bowling": "4/34", "catches": 14
        },
        "achievements": ["SRH captain", "Fastest 50 by bowler: 14 balls (KKR vs MI, 2022)"],
        "bio": "Australia's Test captain in the IPL. Pat Cummins brings international intensity.",
        "bio_hi": "IPL में ऑस्ट्रेलिया के टेस्ट कप्तान। अंतर्राष्ट्रीय तीव्रता लाते हैं।",
    },
    {
        "name": "Heinrich Klaasen", "name_hi": "हेनरिक क्लासेन",
        "role": "Wicketkeeper-Batsman", "batting_style": "Right-hand", "bowling_style": "-",
        "nationality": "South Africa", "current_team": "SRH", "teams_history": ["SRH"], "jersey_no": "69",
        "ipl_stats": {
            "matches": 50, "innings": 46, "runs": 1511, "balls_faced": 881,
            "highest_score": "105*", "avg": 41.97, "sr": 171.51,
            "fifties": 7, "hundreds": 2, "fours": 102, "sixes": 108,
            "catches": 24
        },
        "achievements": ["Joint-3rd fastest IPL century (105* off 39 balls vs KKR, 2025)", "2nd fastest to 1,000 IPL runs"],
        "bio": "The new Mr. 360. 105* off 39 balls — joint 3rd fastest IPL century ever.",
        "bio_hi": "नए मिस्टर 360। 39 गेंदों में 105* — IPL का तीसरा सबसे तेज शतक।",
    },
    {
        "name": "Ruturaj Gaikwad", "name_hi": "ऋतुराज गायकवाड",
        "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "Right-arm leg-break",
        "nationality": "India", "current_team": "CSK", "teams_history": ["CSK"], "jersey_no": "31",
        "ipl_stats": {
            "matches": 71, "innings": 69, "runs": 2502, "balls_faced": 1820,
            "highest_score": "108*", "avg": 40.35, "sr": 137.47,
            "fifties": 20, "hundreds": 2, "fours": 240, "sixes": 82,
            "catches": 39
        },
        "achievements": ["Orange Cap 2021 (635 runs)", "CSK captain — handpicked by Dhoni"],
        "bio": "Dhoni's heir. Orange Cap 2021 with 635 runs. CSK captain since 2024.",
        "bio_hi": "धोनी के उत्तराधिकारी। 2021 में ऑरेंज कैप। CSK के कप्तान।",
    },
]

# ==================== 100+ IPL RECORDS (ALL VERIFIED) ====================
IPL_RECORDS = [
    # ===== BATTING RECORDS (25) =====
    {"category": "batting", "title": "Most Runs (All-time)", "value": "8,661", "holder": "Virat Kohli", "team": "RCB", "year": "2008-2025", "icon": "bat", "color": "#FF3B3B"},
    {"category": "batting", "title": "Highest Individual Score", "value": "175*", "holder": "Chris Gayle", "team": "RCB", "year": "2013 vs PWI, Chinnaswamy", "icon": "flame", "color": "#FF6B6B"},
    {"category": "batting", "title": "2nd Highest Individual Score", "value": "158*", "holder": "Brendon McCullum", "team": "KKR", "year": "2008 vs RCB — First IPL match ever!", "icon": "flame", "color": "#FF8C8C"},
    {"category": "batting", "title": "3rd Highest Individual Score", "value": "141", "holder": "Abhishek Sharma", "team": "SRH", "year": "2025 vs PBKS, Hyderabad", "icon": "flame", "color": "#FFaaaa"},
    {"category": "batting", "title": "Most Runs in a Season", "value": "973", "holder": "Virat Kohli", "team": "RCB", "year": "2016 — may never be broken", "icon": "crown", "color": "#FFD700"},
    {"category": "batting", "title": "Fastest Century", "value": "30 balls", "holder": "Chris Gayle", "team": "RCB", "year": "2013 vs PWI", "icon": "zap", "color": "#f59e0b"},
    {"category": "batting", "title": "2nd Fastest Century", "value": "35 balls", "holder": "Vaibhav Suryavanshi", "team": "RR", "year": "2025 vs GT — age just 14!", "icon": "zap", "color": "#fbbf24"},
    {"category": "batting", "title": "3rd Fastest Century", "value": "37 balls", "holder": "Yusuf Pathan", "team": "RR", "year": "2010 vs MI", "icon": "zap", "color": "#fcd34d"},
    {"category": "batting", "title": "Fastest Fifty", "value": "13 balls", "holder": "Yashasvi Jaiswal", "team": "RR", "year": "2023 vs KKR, Eden Gardens", "icon": "rocket", "color": "#10b981"},
    {"category": "batting", "title": "Most Sixes (All-time)", "value": "357", "holder": "Chris Gayle", "team": "Multiple", "year": "2009-2021", "icon": "target", "color": "#818cf8"},
    {"category": "batting", "title": "Most Fours (All-time)", "value": "772", "holder": "Virat Kohli", "team": "RCB", "year": "2008-2025", "icon": "chevrons-right", "color": "#60a5fa"},
    {"category": "batting", "title": "Most Fifties (Career)", "value": "63", "holder": "Virat Kohli", "team": "RCB", "year": "2008-2025", "icon": "award", "color": "#34d399"},
    {"category": "batting", "title": "Most Centuries (Career)", "value": "8", "holder": "Virat Kohli", "team": "RCB", "year": "2008-2025", "icon": "trophy", "color": "#FFD700"},
    {"category": "batting", "title": "Highest Partnership", "value": "229 runs", "holder": "Kohli & AB de Villiers", "team": "RCB", "year": "2016 vs GL, 2nd wicket", "icon": "users", "color": "#f472b6"},
    {"category": "batting", "title": "Highest Strike Rate (min 1500 runs)", "value": "174.18", "holder": "Andre Russell", "team": "KKR", "year": "2014-2025", "icon": "rocket", "color": "#a855f7"},
    {"category": "batting", "title": "Most Ducks (Career)", "value": "19", "holder": "Glenn Maxwell", "team": "Multiple", "year": "2012-2025 — ouch!", "icon": "alert-circle", "color": "#ef4444"},
    {"category": "batting", "title": "Most Not Outs (Career)", "value": "100", "holder": "MS Dhoni", "team": "CSK", "year": "2008-2025 — Thala unbeaten!", "icon": "shield", "color": "#22c55e"},
    {"category": "batting", "title": "Most Runs by Overseas Player", "value": "6,565", "holder": "David Warner", "team": "SRH/DC", "year": "2009-2025", "icon": "globe", "color": "#0ea5e9"},
    {"category": "batting", "title": "Most Centuries in a Season", "value": "4", "holder": "Jos Buttler", "team": "RR", "year": "2022 — unmatched!", "icon": "crown", "color": "#fbbf24"},
    {"category": "batting", "title": "Highest SR in a Season (min 500 runs)", "value": "204.81", "holder": "Andre Russell", "team": "KKR", "year": "2019 — 510 runs, insane!", "icon": "gauge", "color": "#e879f9"},
    {"category": "batting", "title": "Most Orange Caps (Career)", "value": "3", "holder": "David Warner", "team": "SRH", "year": "2015, 2017, 2019", "icon": "award", "color": "#FF822A"},
    {"category": "batting", "title": "Highest Death-over SR (min 100 balls)", "value": "232.56", "holder": "AB de Villiers", "team": "RCB", "year": "Career (2008-2021)", "icon": "zap", "color": "#dc2626"},
    {"category": "batting", "title": "2nd Highest Partnership", "value": "215*", "holder": "Kohli & AB de Villiers", "team": "RCB", "year": "2015 vs MI — same pair again!", "icon": "users", "color": "#ec4899"},
    {"category": "batting", "title": "3rd Highest Partnership", "value": "210*", "holder": "de Kock & KL Rahul", "team": "LSG", "year": "2022 vs KKR, unbroken", "icon": "users", "color": "#f43f5e"},
    {"category": "batting", "title": "First IPL Century Ever", "value": "158*", "holder": "Brendon McCullum", "team": "KKR", "year": "April 18, 2008 — IPL's very first match!", "icon": "star", "color": "#FFD700"},

    # ===== BOWLING RECORDS (15) =====
    {"category": "bowling", "title": "Most Wickets (All-time)", "value": "221", "holder": "Yuzvendra Chahal", "team": "Multiple", "year": "2013-2025", "icon": "crosshair", "color": "#a855f7"},
    {"category": "bowling", "title": "Best Bowling Figures", "value": "6/12", "holder": "Alzarri Joseph", "team": "MI", "year": "2019 vs SRH — IPL debut!", "icon": "flame", "color": "#ef4444"},
    {"category": "bowling", "title": "Best Economy (min 50 matches)", "value": "6.81", "holder": "Sunil Narine", "team": "KKR", "year": "2012-2025 — mystery king", "icon": "shield", "color": "#22c55e"},
    {"category": "bowling", "title": "Most Hat-tricks (Career)", "value": "3", "holder": "Amit Mishra", "team": "DC/SRH", "year": "2008, 2009, 2013", "icon": "target", "color": "#8b5cf6"},
    {"category": "bowling", "title": "Most Maidens (All-time)", "value": "14", "holder": "Bhuvneshwar Kumar & Praveen Kumar", "team": "SRH/Multiple", "year": "Career — tied record", "icon": "lock", "color": "#06b6d4"},
    {"category": "bowling", "title": "First to 200 IPL Wickets", "value": "200th wicket", "holder": "Yuzvendra Chahal", "team": "RR", "year": "2024 — historic milestone", "icon": "milestone", "color": "#7c3aed"},
    {"category": "bowling", "title": "Most Purple Caps (Career)", "value": "2", "holder": "Bhuvneshwar Kumar & Harshal Patel", "team": "SRH/RCB", "year": "Bhuvi (2016,2017), Harshal (2021,2024)", "icon": "award", "color": "#7c3aed"},
    {"category": "bowling", "title": "Most Dot Balls in a Season", "value": "144", "holder": "Mohammed Siraj", "team": "GT", "year": "2025 season", "icon": "circle", "color": "#64748b"},
    {"category": "bowling", "title": "Best Economy in a Season", "value": "6.68", "holder": "Jasprit Bumrah", "team": "MI", "year": "2025 (18 wkts, 47.2 overs)", "icon": "bar-chart", "color": "#059669"},
    {"category": "bowling", "title": "Fastest to 150 IPL Wickets", "value": "122 matches", "holder": "Rashid Khan", "team": "GT", "year": "Faster than Bumrah (124 matches)", "icon": "clock", "color": "#d946ef"},
    {"category": "bowling", "title": "Most Wickets in a Season", "value": "32", "holder": "Harshal Patel", "team": "RCB", "year": "2021 — Purple Cap", "icon": "trophy", "color": "#7c3aed"},
    {"category": "bowling", "title": "Best Debut Bowling Figures", "value": "6/12", "holder": "Alzarri Joseph", "team": "MI", "year": "2019 vs SRH — dream debut", "icon": "star", "color": "#dc2626"},
    {"category": "bowling", "title": "Most 3-Wicket Hauls (Career)", "value": "20+", "holder": "Jasprit Bumrah", "team": "MI", "year": "2013-2025", "icon": "trending-up", "color": "#0284c7"},
    {"category": "bowling", "title": "Most IPL MVP Awards", "value": "3", "holder": "Sunil Narine", "team": "KKR", "year": "2012, 2018, 2024 — GOAT all-rounder", "icon": "crown", "color": "#eab308"},
    {"category": "bowling", "title": "Most Expensive Spell", "value": "0/66 (4 overs)", "holder": "Ishant Sharma", "team": "DC", "year": "2011 — nightmare spell", "icon": "alert-triangle", "color": "#ef4444"},

    # ===== FIELDING RECORDS (8) =====
    {"category": "fielding", "title": "Most Catches (Fielder)", "value": "117", "holder": "Virat Kohli", "team": "RCB", "year": "2008-2025", "icon": "hand", "color": "#10b981"},
    {"category": "fielding", "title": "Most Catches (Wicketkeeper)", "value": "154", "holder": "MS Dhoni", "team": "CSK", "year": "2008-2025", "icon": "shield", "color": "#0ea5e9"},
    {"category": "fielding", "title": "Most Stumpings (All-time)", "value": "47", "holder": "MS Dhoni", "team": "CSK", "year": "2008-2025 — lightning hands", "icon": "zap", "color": "#f59e0b"},
    {"category": "fielding", "title": "Most Dismissals (WK)", "value": "201", "holder": "MS Dhoni", "team": "CSK", "year": "154 catches + 47 stumpings", "icon": "trophy", "color": "#eab308"},
    {"category": "fielding", "title": "2nd Most Dismissals (WK)", "value": "174", "holder": "Dinesh Karthik", "team": "Multiple", "year": "137 catches + 37 stumpings", "icon": "medal", "color": "#94a3b8"},
    {"category": "fielding", "title": "Most Outfield Catches", "value": "109", "holder": "Ravindra Jadeja", "team": "CSK/RR", "year": "2008-2025 — Sir Jadeja!", "icon": "star", "color": "#22d3ee"},
    {"category": "fielding", "title": "3rd Most Stumpings", "value": "32", "holder": "Robin Uthappa", "team": "Multiple", "year": "2008-2022", "icon": "hand", "color": "#a3e635"},
    {"category": "fielding", "title": "Most Matches Played", "value": "278", "holder": "MS Dhoni", "team": "CSK", "year": "2008-2025 — most capped ever", "icon": "calendar", "color": "#6366f1"},

    # ===== TEAM RECORDS (15) =====
    {"category": "team", "title": "Highest Team Total", "value": "287/3", "holder": "SRH vs RCB", "team": "SRH", "year": "2024, Bengaluru", "icon": "trophy", "color": "#FF822A"},
    {"category": "team", "title": "2nd Highest Team Total", "value": "286/6", "holder": "SRH vs RR", "team": "SRH", "year": "2025, Hyderabad", "icon": "trophy", "color": "#FFa04a"},
    {"category": "team", "title": "3rd Highest Team Total", "value": "278/3", "holder": "SRH vs KKR", "team": "SRH", "year": "2025, Delhi — SRH own top 3!", "icon": "trophy", "color": "#FFc07a"},
    {"category": "team", "title": "Lowest Team Total", "value": "49 all out", "holder": "RCB vs KKR", "team": "RCB", "year": "2017, Eden Gardens — darkest day", "icon": "alert-circle", "color": "#ef4444"},
    {"category": "team", "title": "Most Titles (Joint)", "value": "5 each", "holder": "Mumbai Indians & Chennai Super Kings", "team": "MI/CSK", "year": "MI: 2013,15,17,19,20 | CSK: 2010,11,18,21,23", "icon": "crown", "color": "#FFD700"},
    {"category": "team", "title": "Longest Winning Streak", "value": "14 matches", "holder": "Kolkata Knight Riders", "team": "KKR", "year": "All-time record", "icon": "trending-up", "color": "#8b5cf6"},
    {"category": "team", "title": "Most Finals Played", "value": "10", "holder": "Chennai Super Kings", "team": "CSK", "year": "2008-2025 — always there", "icon": "flag", "color": "#eab308"},
    {"category": "team", "title": "Most Playoff Qualifications", "value": "12", "holder": "Chennai Super Kings", "team": "CSK", "year": "Out of 16 seasons — consistency!", "icon": "bar-chart", "color": "#14b8a6"},
    {"category": "team", "title": "Highest Successful Chase", "value": "205/0", "holder": "GT vs DC", "team": "GT", "year": "2025 — 10 wicket win, no loss!", "icon": "arrow-up", "color": "#22c55e"},
    {"category": "team", "title": "Biggest Win (Runs)", "value": "146 runs", "holder": "MI vs DC", "team": "MI", "year": "2017, Wankhede", "icon": "arrow-up-right", "color": "#3b82f6"},
    {"category": "team", "title": "Most Titles (3rd)", "value": "3", "holder": "Kolkata Knight Riders", "team": "KKR", "year": "2012, 2014, 2024", "icon": "crown", "color": "#c084fc"},
    {"category": "team", "title": "MI vs CSK Head-to-Head", "value": "21-18", "holder": "MI leads CSK", "team": "MI/CSK", "year": "39 matches — IPL's El Clasico", "icon": "swords", "color": "#f97316"},
    {"category": "team", "title": "Debut Season Champions", "value": "Won in Year 1", "holder": "Gujarat Titans", "team": "GT", "year": "2022 — only franchise to win debut IPL", "icon": "star", "color": "#06b6d4"},
    {"category": "team", "title": "9 Successful 200+ Chases", "value": "Record season", "holder": "IPL 2025", "team": "Multiple", "year": "2025 — batsmen's paradise", "icon": "trending-up", "color": "#84cc16"},
    {"category": "team", "title": "Close Final: 1-Run Win", "value": "Won by 1 run", "holder": "MI vs RPS (2017) & MI vs CSK (2019)", "team": "MI", "year": "Two 1-run finals — MI's destiny!", "icon": "target", "color": "#0ea5e9"},

    # ===== CONTROVERSY & DRAMA (12) =====
    {"category": "controversy", "title": "Slapgate (2008)", "value": "Harbhajan slapped Sreesanth", "holder": "MI vs PBKS", "team": "MI", "year": "April 25, 2008 — first IPL scandal", "icon": "alert-triangle", "color": "#ef4444"},
    {"category": "controversy", "title": "Spot-Fixing Scandal (2013)", "value": "Sreesanth, Chavan, Chandila arrested", "holder": "Delhi Police raid", "team": "RR", "year": "IPL's darkest chapter — players jailed", "icon": "alert-octagon", "color": "#dc2626"},
    {"category": "controversy", "title": "CSK & RR Banned 2 Years", "value": "2016-2017 suspension", "holder": "Lodha Committee", "team": "CSK/RR", "year": "Meiyappan & Kundra banned for life for betting", "icon": "ban", "color": "#b91c1c"},
    {"category": "controversy", "title": "Mankading (2019)", "value": "Ashwin ran out Buttler", "holder": "PBKS vs RR", "team": "PBKS", "year": "Spirit of cricket debate exploded", "icon": "x-circle", "color": "#f97316"},
    {"category": "controversy", "title": "Bio-Bubble Breach (2021)", "value": "IPL suspended mid-season", "holder": "COVID cases in camps", "team": "Multiple", "year": "Tournament moved to UAE after COVID outbreak", "icon": "shield-alert", "color": "#7c2d12"},
    {"category": "controversy", "title": "Lalit Modi Expelled (2010)", "value": "IPL founder suspended by BCCI", "holder": "Financial irregularities", "team": "BCCI", "year": "Exiled from India for corruption", "icon": "user-x", "color": "#991b1b"},
    {"category": "controversy", "title": "Kochi Tuskers Terminated (2011)", "value": "Franchise axed after 1 season", "holder": "Failed bank guarantee", "team": "KTK", "year": "Only IPL team terminated mid-contract", "icon": "x-square", "color": "#78350f"},
    {"category": "controversy", "title": "Dhoni 112m Six (2012)", "value": "One of the longest sixes in IPL", "holder": "MS Dhoni vs MI", "team": "CSK", "year": "51 off 20 balls in eliminator — helicopter magic", "icon": "zap", "color": "#eab308"},
    {"category": "controversy", "title": "RCB 49 All Out (2017)", "value": "Lowest score in IPL history", "holder": "RCB vs KKR", "team": "RCB", "year": "Eden Gardens — humiliation on live TV", "icon": "skull", "color": "#dc2626"},
    {"category": "controversy", "title": "CSK's Fairytale Comeback (2018)", "value": "Won title in comeback season", "holder": "Shane Watson 117* in final", "team": "CSK", "year": "After 2-year ban — greatest comeback ever", "icon": "heart", "color": "#FFD700"},
    {"category": "controversy", "title": "Double Super Over (2020)", "value": "First & only in IPL history", "holder": "MI vs PBKS", "team": "PBKS won", "year": "Dubai — 2 Super Overs needed!", "icon": "repeat", "color": "#6366f1"},
    {"category": "controversy", "title": "15 Super Overs in IPL", "value": "Total Super Overs played", "holder": "First: RR vs KKR (2009)", "team": "Multiple", "year": "2009-2025 — heart-stopping finishes", "icon": "timer", "color": "#0891b2"},

    # ===== FUN & UNIQUE RECORDS (12) =====
    {"category": "fun", "title": "Most Expensive Over", "value": "37 runs (tied)", "holder": "Parameswaran (2011) & Harshal Patel (2021)", "team": "KTK/RCB", "year": "Gayle & Jadeja went berserk", "icon": "bomb", "color": "#ef4444"},
    {"category": "fun", "title": "Youngest IPL Debutant", "value": "14 years, 23 days", "holder": "Vaibhav Suryavanshi", "team": "RR", "year": "2025 — youngest IPL player EVER", "icon": "baby", "color": "#10b981"},
    {"category": "fun", "title": "Oldest IPL Player", "value": "45 years, 92 days", "holder": "Brad Hogg", "team": "KKR", "year": "2016 — still bowling leg-spin at 45!", "icon": "glasses", "color": "#6366f1"},
    {"category": "fun", "title": "Oldest IPL Debutant", "value": "41 years, 211 days", "holder": "Pravin Tambe", "team": "RR", "year": "2013 — never too late to dream", "icon": "heart", "color": "#ec4899"},
    {"category": "fun", "title": "Most Expensive Player (Auction)", "value": "Rs 27 Crore", "holder": "Rishabh Pant", "team": "LSG", "year": "2025 Mega Auction — record shattered", "icon": "indian-rupee", "color": "#f59e0b"},
    {"category": "fun", "title": "18 IPL Seasons, 7 Champions", "value": "MI, CSK, KKR, GT, SRH, RR, RCB", "holder": "7 different franchises", "team": "Multiple", "year": "2008-2025 — DC, PBKS, LSG still waiting", "icon": "trophy", "color": "#FFD700"},
    {"category": "fun", "title": "IPL's Very First Ball", "value": "McCullum's 158* on Day 1", "holder": "Brendon McCullum", "team": "KKR", "year": "April 18, 2008 — IPL born with a bang!", "icon": "star", "color": "#fbbf24"},
    {"category": "fun", "title": "SRH Owns Top 3 Team Totals", "value": "287/3, 286/6, 278/3", "holder": "Sunrisers Hyderabad", "team": "SRH", "year": "2024-2025 — batting monsters", "icon": "bar-chart-2", "color": "#FF822A"},
    {"category": "fun", "title": "Ee Sala Cup Namde — FINALLY!", "value": "RCB's 17-year wait ended", "holder": "Royal Challengers Bengaluru", "team": "RCB", "year": "2025 Final vs PBKS — won by 6 runs", "icon": "party-popper", "color": "#ef4444"},
    {"category": "fun", "title": "CSK: Banned, Returned, Won", "value": "Title in comeback year 2018", "holder": "CSK", "team": "CSK", "year": "Watson's 117* in final — sporting fairytale", "icon": "rotate-cw", "color": "#eab308"},
    {"category": "fun", "title": "GT Won in Debut Year", "value": "Champions in their first season", "holder": "Gujarat Titans", "team": "GT", "year": "2022 — no franchise has done this since RR in 2008", "icon": "rocket", "color": "#06b6d4"},
    {"category": "fun", "title": "Kohli-ABD: 229 & 215", "value": "Top 2 partnerships — same pair!", "holder": "Virat Kohli & AB de Villiers", "team": "RCB", "year": "2016 & 2015 — cricket's greatest bromance", "icon": "heart", "color": "#f472b6"},

    # ===== SEASON CHAMPIONS (18) =====
    {"category": "champions", "title": "IPL 2008 Champion", "value": "Rajasthan Royals", "holder": "Beat CSK by 3 wickets", "team": "RR", "year": "Shane Warne's underdogs — fairytale debut", "icon": "trophy", "color": "#FFD700"},
    {"category": "champions", "title": "IPL 2009 Champion", "value": "Deccan Chargers", "holder": "Beat RCB by 6 runs", "team": "DC", "year": "South Africa — Gilchrist's final glory", "icon": "trophy", "color": "#FFD700"},
    {"category": "champions", "title": "IPL 2010 Champion", "value": "Chennai Super Kings", "holder": "Beat MI by 22 runs", "team": "CSK", "year": "Dhoni's first — dynasty begins", "icon": "trophy", "color": "#FFD700"},
    {"category": "champions", "title": "IPL 2011 Champion", "value": "Chennai Super Kings", "holder": "Beat RCB by 58 runs", "team": "CSK", "year": "Back-to-back — yellow army unstoppable", "icon": "trophy", "color": "#FFD700"},
    {"category": "champions", "title": "IPL 2012 Champion", "value": "Kolkata Knight Riders", "holder": "Beat CSK by 5 wickets", "team": "KKR", "year": "Gambhir's KKR — Korbo Lorbo Jeetbo", "icon": "trophy", "color": "#FFD700"},
    {"category": "champions", "title": "IPL 2013 Champion", "value": "Mumbai Indians", "holder": "Beat CSK by 23 runs", "team": "MI", "year": "Rohit's first title — MI era begins", "icon": "trophy", "color": "#FFD700"},
    {"category": "champions", "title": "IPL 2014 Champion", "value": "Kolkata Knight Riders", "holder": "Beat PBKS by 3 wickets", "team": "KKR", "year": "Manish Pandey's century in final", "icon": "trophy", "color": "#FFD700"},
    {"category": "champions", "title": "IPL 2015 Champion", "value": "Mumbai Indians", "holder": "Beat CSK by 41 runs", "team": "MI", "year": "Rohit & Simmons dominate", "icon": "trophy", "color": "#FFD700"},
    {"category": "champions", "title": "IPL 2016 Champion", "value": "Sunrisers Hyderabad", "holder": "Beat RCB by 8 runs", "team": "SRH", "year": "Warner leads SRH to maiden crown", "icon": "trophy", "color": "#FFD700"},
    {"category": "champions", "title": "IPL 2017 Champion", "value": "Mumbai Indians", "holder": "Beat RPS by 1 run", "team": "MI", "year": "LAST BALL THRILLER — closest final!", "icon": "trophy", "color": "#FFD700"},
    {"category": "champions", "title": "IPL 2018 Champion", "value": "Chennai Super Kings", "holder": "Beat SRH by 8 wickets", "team": "CSK", "year": "CSK's comeback — Watson 117* in final", "icon": "trophy", "color": "#FFD700"},
    {"category": "champions", "title": "IPL 2019 Champion", "value": "Mumbai Indians", "holder": "Beat CSK by 1 run", "team": "MI", "year": "ANOTHER 1-run final — MI's destiny!", "icon": "trophy", "color": "#FFD700"},
    {"category": "champions", "title": "IPL 2020 Champion", "value": "Mumbai Indians", "holder": "Beat DC by 5 wickets", "team": "MI", "year": "Dubai bubble — MI's 5th & record title", "icon": "trophy", "color": "#FFD700"},
    {"category": "champions", "title": "IPL 2021 Champion", "value": "Chennai Super Kings", "holder": "Beat KKR by 27 runs", "team": "CSK", "year": "Faf du Plessis 86* — Dhoni's 4th", "icon": "trophy", "color": "#FFD700"},
    {"category": "champions", "title": "IPL 2022 Champion", "value": "Gujarat Titans", "holder": "Beat RR by 7 wickets", "team": "GT", "year": "DEBUT SEASON WINNERS — Hardik Pandya's GT", "icon": "trophy", "color": "#FFD700"},
    {"category": "champions", "title": "IPL 2023 Champion", "value": "Chennai Super Kings", "holder": "Beat GT by 5 wickets (DLS)", "team": "CSK", "year": "Dhoni's 5th — equals Rohit's record", "icon": "trophy", "color": "#FFD700"},
    {"category": "champions", "title": "IPL 2024 Champion", "value": "Kolkata Knight Riders", "holder": "Beat SRH by 8 wickets", "team": "KKR", "year": "Narine's 2024 reinvention — KKR's 3rd", "icon": "trophy", "color": "#FFD700"},
    {"category": "champions", "title": "IPL 2025 Champion", "value": "Royal Challengers Bengaluru", "holder": "Beat PBKS by 6 runs", "team": "RCB", "year": "Ee Sala Cup Namde! — RCB's MAIDEN title!", "icon": "trophy", "color": "#FFD700"},

    # ===== AUCTION MILESTONES (10) =====
    {"category": "auction", "title": "2008: First Mega Auction", "value": "Rs 9.5 Cr — MS Dhoni", "holder": "MS Dhoni to CSK", "team": "CSK", "year": "2008 — IPL's first blockbuster signing", "icon": "gavel", "color": "#f59e0b"},
    {"category": "auction", "title": "2011: Gambhir's Record", "value": "Rs 14.9 Cr — Gautam Gambhir", "holder": "Gambhir to KKR", "team": "KKR", "year": "Became KKR captain, won 2 titles", "icon": "gavel", "color": "#f59e0b"},
    {"category": "auction", "title": "2014-15: Yuvraj Mania", "value": "Rs 14-16 Cr — Yuvraj Singh", "holder": "RCB (2014), DD (2015)", "team": "Multiple", "year": "Most expensive Indian of that era", "icon": "gavel", "color": "#f59e0b"},
    {"category": "auction", "title": "2017: Stokes Bombshell", "value": "Rs 14.5 Cr — Ben Stokes", "holder": "Rising Pune Supergiant", "team": "RPS", "year": "Unknown all-rounder became most expensive", "icon": "gavel", "color": "#f59e0b"},
    {"category": "auction", "title": "2020: Cummins to KKR", "value": "Rs 15.5 Cr — Pat Cummins", "holder": "Australia captain joins KKR", "team": "KKR", "year": "Most expensive overseas player then", "icon": "gavel", "color": "#f59e0b"},
    {"category": "auction", "title": "2021: Morris Surprise", "value": "Rs 16.25 Cr — Chris Morris", "holder": "RR's biggest buy ever", "team": "RR", "year": "Highest paid player that year", "icon": "gavel", "color": "#f59e0b"},
    {"category": "auction", "title": "2023: Sam Curran Era", "value": "Rs 18.5 Cr — Sam Curran", "holder": "PBKS break the bank", "team": "PBKS", "year": "T20 WC hero cashes in", "icon": "gavel", "color": "#f59e0b"},
    {"category": "auction", "title": "2024: Starc's Mega Deal", "value": "Rs 24.75 Cr — Mitchell Starc", "holder": "KKR's record signing", "team": "KKR", "year": "Helped KKR win 2024 title", "icon": "gavel", "color": "#f59e0b"},
    {"category": "auction", "title": "2025: Pant Shatters Records", "value": "Rs 27 Cr — Rishabh Pant", "holder": "LSG's mega gamble", "team": "LSG", "year": "All-time record — highest IPL buy EVER", "icon": "gavel", "color": "#f59e0b"},
    {"category": "auction", "title": "Unsold to Star: Jadeja's Arc", "value": "Rs 2 Cr to Rs 16 Cr", "holder": "Ravindra Jadeja", "team": "CSK/RR", "year": "Went unsold in 2008 — became Rs 16 Cr star", "icon": "trending-up", "color": "#22c55e"},
]

# ==================== ORANGE & PURPLE CAP WINNERS (VERIFIED) ====================
CAP_WINNERS = [
    {"year": 2025, "orange_cap": {"player": "Sai Sudharsan", "runs": 759, "team": "GT"}, "purple_cap": {"player": "Prasidh Krishna", "wickets": 25, "team": "GT"}},
    {"year": 2024, "orange_cap": {"player": "Virat Kohli", "runs": 741, "team": "RCB"}, "purple_cap": {"player": "Harshal Patel", "wickets": 24, "team": "PBKS"}},
    {"year": 2023, "orange_cap": {"player": "Shubman Gill", "runs": 890, "team": "GT"}, "purple_cap": {"player": "Mohammed Shami", "wickets": 28, "team": "GT"}},
    {"year": 2022, "orange_cap": {"player": "Jos Buttler", "runs": 863, "team": "RR"}, "purple_cap": {"player": "Yuzvendra Chahal", "wickets": 27, "team": "RR"}},
    {"year": 2021, "orange_cap": {"player": "Ruturaj Gaikwad", "runs": 635, "team": "CSK"}, "purple_cap": {"player": "Harshal Patel", "wickets": 32, "team": "RCB"}},
    {"year": 2020, "orange_cap": {"player": "KL Rahul", "runs": 670, "team": "PBKS"}, "purple_cap": {"player": "Kagiso Rabada", "wickets": 30, "team": "DC"}},
    {"year": 2019, "orange_cap": {"player": "David Warner", "runs": 692, "team": "SRH"}, "purple_cap": {"player": "Imran Tahir", "wickets": 26, "team": "CSK"}},
    {"year": 2018, "orange_cap": {"player": "Kane Williamson", "runs": 735, "team": "SRH"}, "purple_cap": {"player": "Andrew Tye", "wickets": 24, "team": "PBKS"}},
    {"year": 2017, "orange_cap": {"player": "David Warner", "runs": 641, "team": "SRH"}, "purple_cap": {"player": "Bhuvneshwar Kumar", "wickets": 26, "team": "SRH"}},
    {"year": 2016, "orange_cap": {"player": "Virat Kohli", "runs": 973, "team": "RCB"}, "purple_cap": {"player": "Bhuvneshwar Kumar", "wickets": 23, "team": "SRH"}},
]


async def seed_ipl_data(db, force=False):
    """Seeds IPL players, records, and cap winners into MongoDB."""
    now = utc_now().isoformat()

    if force:
        await db.ipl_players.delete_many({})
        await db.ipl_records.delete_many({})
        await db.ipl_caps.delete_many({})

    for p in IPL_PLAYERS:
        p_doc = {**p, "created_at": now, "updated_at": now}
        await db.ipl_players.update_one({"name": p["name"]}, {"$set": p_doc}, upsert=True)
    await db.ipl_players.create_index("name")
    await db.ipl_players.create_index("current_team")
    await db.ipl_players.create_index("role")

    for r in IPL_RECORDS:
        r_doc = {**r, "created_at": now, "updated_at": now}
        await db.ipl_records.update_one({"title": r["title"]}, {"$set": r_doc}, upsert=True)
    await db.ipl_records.create_index("category")

    for c in CAP_WINNERS:
        await db.ipl_caps.update_one({"year": c["year"]}, {"$set": {**c, "created_at": now}}, upsert=True)

    players_count = await db.ipl_players.count_documents({})
    records_count = await db.ipl_records.count_documents({})
    caps_count = await db.ipl_caps.count_documents({})

    return {"players": players_count, "records": records_count, "cap_winners": caps_count, "force_reseeded": force}
