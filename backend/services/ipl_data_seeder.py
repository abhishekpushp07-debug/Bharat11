"""
IPL Encyclopedia Data Seeder
Seeds comprehensive IPL player profiles, records, and venue data into MongoDB.
"""
import asyncio
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)

# ==================== IPL PLAYERS DATABASE ====================
IPL_PLAYERS = [
    # === BATSMEN ===
    {"name": "Virat Kohli", "name_hi": "विराट कोहली", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "Right-arm medium", "nationality": "India",
     "current_team": "RCB", "teams_history": ["RCB"], "jersey_no": "18",
     "ipl_stats": {"matches": 252, "runs": 8004, "balls": 5765, "highest_score": "113", "avg": 37.25, "sr": 131.61, "fifties": 55, "hundreds": 8, "fours": 706, "sixes": 262, "wickets": 4, "catches": 122},
     "achievements": ["Most runs in a single IPL season (973 in 2016)", "Only player with 8 IPL centuries", "Most 50+ scores in IPL history", "Orange Cap 2016"],
     "bio": "The King of IPL batting. Virat Kohli has been the heartbeat of RCB since 2008, becoming the franchise's all-time leading run-scorer and the highest run-scorer in IPL history.",
     "bio_hi": "IPL बल्लेबाजी के किंग। विराट कोहली 2008 से RCB की धड़कन रहे हैं — IPL इतिहास में सर्वाधिक रन बनाने वाले बल्लेबाज।"},
    {"name": "Rohit Sharma", "name_hi": "रोहित शर्मा", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "Right-arm off-break", "nationality": "India",
     "current_team": "MI", "teams_history": ["DC", "MI"], "jersey_no": "45",
     "ipl_stats": {"matches": 243, "runs": 6211, "balls": 4493, "highest_score": "109*", "avg": 29.58, "sr": 130.39, "fifties": 42, "hundreds": 2, "fours": 530, "sixes": 271, "wickets": 15, "catches": 68},
     "achievements": ["Most IPL titles as captain (5)", "One of only 2 players to play for same franchise 15+ seasons", "Hitman - known for clean hitting"],
     "bio": "The Hitman. Rohit Sharma is the most successful captain in IPL history with 5 titles for Mumbai Indians. His elegant pull shots and timing are iconic.",
     "bio_hi": "हिटमैन। रोहित शर्मा IPL इतिहास के सबसे सफल कप्तान हैं — मुंबई इंडियंस के लिए 5 खिताब।"},
    {"name": "MS Dhoni", "name_hi": "एमएस धोनी", "role": "Wicketkeeper-Batsman", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "India",
     "current_team": "CSK", "teams_history": ["CSK", "RPS"], "jersey_no": "7",
     "ipl_stats": {"matches": 264, "runs": 5243, "balls": 3827, "highest_score": "84*", "avg": 39.13, "sr": 135.20, "fifties": 24, "hundreds": 0, "fours": 360, "sixes": 249, "wickets": 0, "catches": 152, "stumpings": 43},
     "achievements": ["Most IPL titles as captain (5 with CSK)", "Most matches as IPL captain", "Thala for a reason", "Greatest finisher in T20 history"],
     "bio": "Captain Cool. MS Dhoni is the greatest captain and finisher in IPL history. His helicopter shot and calm demeanor under pressure are legendary.",
     "bio_hi": "कैप्टन कूल। एमएस धोनी IPL इतिहास के सबसे महान कप्तान और फिनिशर हैं। उनका हेलीकॉप्टर शॉट और शांत स्वभाव दिग्गज है।"},
    {"name": "Suryakumar Yadav", "name_hi": "सूर्यकुमार यादव", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "Right-arm medium", "nationality": "India",
     "current_team": "MI", "teams_history": ["MI", "KKR"], "jersey_no": "63",
     "ipl_stats": {"matches": 163, "runs": 3970, "balls": 2790, "highest_score": "103*", "avg": 31.27, "sr": 145.57, "fifties": 24, "hundreds": 1, "fours": 358, "sixes": 189, "wickets": 0, "catches": 50},
     "achievements": ["360-degree player", "Mr. 360 of Indian cricket", "ICC T20I Player of the Year"],
     "bio": "SKY - the 360-degree player. Suryakumar Yadav can hit any ball to any part of the ground, making him one of the most entertaining batsmen in T20 cricket.",
     "bio_hi": "SKY — 360-डिग्री खिलाड़ी। सूर्यकुमार यादव किसी भी गेंद को मैदान के किसी भी हिस्से में मार सकते हैं।"},
    {"name": "David Warner", "name_hi": "डेविड वॉर्नर", "role": "Batsman", "batting_style": "Left-hand", "bowling_style": "-", "nationality": "Australia",
     "current_team": "DC", "teams_history": ["DC", "SRH"], "jersey_no": "31",
     "ipl_stats": {"matches": 176, "runs": 6565, "balls": 4614, "highest_score": "126", "avg": 41.20, "sr": 139.96, "fifties": 44, "hundreds": 4, "fours": 644, "sixes": 227, "wickets": 0, "catches": 52},
     "achievements": ["4x Orange Cap winner", "Most runs by overseas player in IPL", "Fastest to 1000 IPL runs"],
     "bio": "The Bull. David Warner is the most prolific overseas run-scorer in IPL history with 4 Orange Caps. His aggressive left-handed batting terrorized bowlers for SRH.",
     "bio_hi": "द बुल। डेविड वॉर्नर IPL इतिहास में सबसे ज्यादा रन बनाने वाले विदेशी खिलाड़ी हैं — 4 ऑरेंज कैप।"},
    {"name": "Shubman Gill", "name_hi": "शुभमन गिल", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "India",
     "current_team": "GT", "teams_history": ["KKR", "GT"], "jersey_no": "77",
     "ipl_stats": {"matches": 101, "runs": 3161, "balls": 2280, "highest_score": "129", "avg": 35.90, "sr": 134.09, "fifties": 21, "hundreds": 3, "fours": 294, "sixes": 104, "wickets": 0, "catches": 28},
     "achievements": ["Youngest GT captain", "Fastest GT century", "ICC Emerging Cricketer of the Year"],
     "bio": "Prince of Indian cricket. Shubman Gill's elegant batting style and composure beyond his years make him the future of Indian cricket.",
     "bio_hi": "भारतीय क्रिकेट के राजकुमार। शुभमन गिल की शानदार बल्लेबाजी और उम्र से परे परिपक्वता उन्हें भारतीय क्रिकेट का भविष्य बनाती है।"},
    {"name": "Jos Buttler", "name_hi": "जोस बटलर", "role": "Wicketkeeper-Batsman", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "England",
     "current_team": "RR", "teams_history": ["MI", "RR"], "jersey_no": "63",
     "ipl_stats": {"matches": 82, "runs": 2831, "balls": 1870, "highest_score": "124", "avg": 38.78, "sr": 150.32, "fifties": 14, "hundreds": 4, "fours": 228, "sixes": 148, "wickets": 0, "catches": 32},
     "achievements": ["4 centuries in IPL 2022", "Orange Cap 2022 (863 runs)", "Fastest RR century"],
     "bio": "The Englishman who broke IPL records. Jos Buttler's 2022 season for RR with 4 centuries was one of the greatest individual seasons in IPL history.",
     "bio_hi": "वो इंग्लिश बल्लेबाज जिसने IPL के रिकॉर्ड तोड़ दिए। जोस बटलर का 2022 सीजन 4 शतकों के साथ IPL इतिहास का सबसे शानदार सीजन था।"},
    {"name": "Yashasvi Jaiswal", "name_hi": "यशस्वी जायसवाल", "role": "Batsman", "batting_style": "Left-hand", "bowling_style": "Right-arm leg-break", "nationality": "India",
     "current_team": "RR", "teams_history": ["RR"], "jersey_no": "12",
     "ipl_stats": {"matches": 55, "runs": 1632, "balls": 1120, "highest_score": "124*", "avg": 32.64, "sr": 158.57, "fifties": 7, "hundreds": 2, "fours": 174, "sixes": 75, "wickets": 0, "catches": 18},
     "achievements": ["Youngest player to score a List A double century", "Emerging Player Award nominee"],
     "bio": "From selling panipuri on Mumbai streets to IPL stardom. Yashasvi Jaiswal's rags-to-riches story is the most inspiring in Indian cricket.",
     "bio_hi": "मुंबई की सड़कों पर पानीपुरी बेचने से IPL स्टारडम तक। यशस्वी जायसवाल की कहानी भारतीय क्रिकेट की सबसे प्रेरक कहानी है।"},
    # === BOWLERS ===
    {"name": "Jasprit Bumrah", "name_hi": "जसप्रीत बुमराह", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm fast", "nationality": "India",
     "current_team": "MI", "teams_history": ["MI"], "jersey_no": "93",
     "ipl_stats": {"matches": 120, "runs": 56, "balls": 2832, "highest_score": "10*", "avg": 0, "sr": 0, "fifties": 0, "hundreds": 0, "fours": 0, "sixes": 0, "wickets": 145, "economy": 7.39, "best_bowling": "5/10", "catches": 12},
     "achievements": ["Best economy rate in IPL death overs", "Most yorkers in IPL history", "Discovered by MI scouts at 19"],
     "bio": "The yorker king. Jasprit Bumrah's unorthodox action and lethal yorkers make him the deadliest fast bowler in IPL history.",
     "bio_hi": "यॉर्कर किंग। जसप्रीत बुमराह की अनोखी एक्शन और घातक यॉर्कर उन्हें IPL इतिहास का सबसे खतरनाक तेज गेंदबाज बनाती है।"},
    {"name": "Yuzvendra Chahal", "name_hi": "युजवेंद्र चहल", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm leg-break", "nationality": "India",
     "current_team": "RR", "teams_history": ["MI", "RCB", "RR"], "jersey_no": "3",
     "ipl_stats": {"matches": 145, "runs": 64, "balls": 3240, "highest_score": "8", "avg": 0, "sr": 0, "fifties": 0, "hundreds": 0, "fours": 2, "sixes": 3, "wickets": 187, "economy": 7.62, "best_bowling": "5/40", "catches": 26},
     "achievements": ["Most wickets in IPL history", "Purple Cap 2022", "First player to take 150 IPL wickets"],
     "bio": "The spider. Yuzvendra Chahal's web of leg-spin has trapped more IPL batsmen than any other bowler in history — the all-time leading wicket-taker.",
     "bio_hi": "स्पाइडर। युजवेंद्र चहल के लेग-स्पिन के जाल ने IPL इतिहास में सबसे ज्यादा बल्लेबाजों को फंसाया — सर्वकालीन सर्वाधिक विकेट लेने वाले।"},
    {"name": "Rashid Khan", "name_hi": "रशीद खान", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm leg-break", "nationality": "Afghanistan",
     "current_team": "GT", "teams_history": ["SRH", "GT"], "jersey_no": "19",
     "ipl_stats": {"matches": 106, "runs": 404, "balls": 2376, "highest_score": "34*", "avg": 0, "sr": 0, "fifties": 0, "hundreds": 0, "fours": 18, "sixes": 25, "wickets": 112, "economy": 6.34, "best_bowling": "4/24", "catches": 22},
     "achievements": ["Best economy in IPL history (min 50 matches)", "GT's trump card", "Youngest captain in IPL"],
     "bio": "The Afghan prodigy. Rashid Khan's leg-spin is virtually unplayable — he has the best economy rate of any significant bowler in IPL history.",
     "bio_hi": "अफगान प्रॉडिजी। रशीद खान की लेग-स्पिन लगभग नाखेलने योग्य है — IPL इतिहास में सबसे अच्छी इकॉनमी रेट।"},
    {"name": "Sunil Narine", "name_hi": "सुनील नरेन", "role": "All-rounder", "batting_style": "Left-hand", "bowling_style": "Right-arm off-break", "nationality": "West Indies",
     "current_team": "KKR", "teams_history": ["KKR"], "jersey_no": "75",
     "ipl_stats": {"matches": 164, "runs": 1560, "balls": 1020, "highest_score": "109", "avg": 15.75, "sr": 168.12, "fifties": 3, "hundreds": 1, "fours": 105, "sixes": 126, "wickets": 163, "economy": 6.67, "best_bowling": "5/19", "catches": 28},
     "achievements": ["Mystery spinner who revolutionized T20 bowling", "IPL's most impactful all-rounder", "3 IPL titles with KKR"],
     "bio": "The mystery man. Sunil Narine changed T20 cricket with his impossible-to-read off-spin and evolved into a destructive opening batsman.",
     "bio_hi": "मिस्ट्री मैन। सुनील नरेन ने अपनी रहस्यमय ऑफ-स्पिन से T20 क्रिकेट बदल दिया और विनाशकारी ओपनर भी बन गए।"},
    {"name": "Ravindra Jadeja", "name_hi": "रवींद्र जडेजा", "role": "All-rounder", "batting_style": "Left-hand", "bowling_style": "Left-arm orthodox", "nationality": "India",
     "current_team": "CSK", "teams_history": ["RR", "KTK", "CSK"], "jersey_no": "8",
     "ipl_stats": {"matches": 210, "runs": 2692, "balls": 1980, "highest_score": "62*", "avg": 26.39, "sr": 131.84, "fifties": 4, "hundreds": 0, "fours": 179, "sixes": 124, "wickets": 147, "economy": 7.60, "best_bowling": "5/16", "catches": 79},
     "achievements": ["Sir Jadeja - greatest fielder in IPL", "Triple threat: bat, ball, field", "5 IPL titles"],
     "bio": "Sir Jadeja. The greatest fielder in IPL history who can win games with bat, ball, or in the field. A true CSK legend.",
     "bio_hi": "सर जडेजा। IPL इतिहास के सबसे महान फील्डर जो बल्ले, गेंद या मैदान से मैच जिता सकते हैं। सच्चे CSK लीजेंड।"},
    {"name": "Andre Russell", "name_hi": "आंद्रे रसेल", "role": "All-rounder", "batting_style": "Right-hand", "bowling_style": "Right-arm fast", "nationality": "West Indies",
     "current_team": "KKR", "teams_history": ["DC", "KKR"], "jersey_no": "12",
     "ipl_stats": {"matches": 107, "runs": 2035, "balls": 1156, "highest_score": "88*", "avg": 29.07, "sr": 177.16, "fifties": 8, "hundreds": 0, "fours": 127, "sixes": 174, "wickets": 70, "economy": 9.15, "best_bowling": "3/19", "catches": 35},
     "achievements": ["Highest strike rate in IPL (min 500 runs): 177+", "Most destructive T20 hitter ever", "MVP Award winner"],
     "bio": "Dre Russ. The most destructive hitter in IPL history. Andre Russell's power hitting has won KKR countless unwinnable games.",
     "bio_hi": "ड्रे रस। IPL इतिहास का सबसे विनाशकारी हिटर। आंद्रे रसेल की पावर हिटिंग ने KKR के लिए अनगिनत नामुमकिन मैच जिताए।"},
    {"name": "Chris Gayle", "name_hi": "क्रिस गेल", "role": "Batsman", "batting_style": "Left-hand", "bowling_style": "Left-arm off-break", "nationality": "West Indies",
     "current_team": "-", "teams_history": ["KKR", "RCB", "PBKS"], "jersey_no": "175",
     "ipl_stats": {"matches": 142, "runs": 4965, "balls": 3090, "highest_score": "175*", "avg": 39.72, "sr": 148.96, "fifties": 22, "hundreds": 6, "fours": 357, "sixes": 357, "wickets": 22, "economy": 8.30, "best_bowling": "2/5", "catches": 34},
     "achievements": ["Highest individual IPL score: 175* vs PWI", "Universe Boss", "Most sixes in IPL history (357)", "Fastest IPL century (30 balls)"],
     "bio": "Universe Boss. Chris Gayle redefined power hitting in T20 cricket. His 175* remains the highest individual score in IPL history — a record that may never be broken.",
     "bio_hi": "यूनिवर्स बॉस। क्रिस गेल ने T20 क्रिकेट में पावर हिटिंग को नया अर्थ दिया। उनका 175* IPL का सर्वोच्च व्यक्तिगत स्कोर है।"},
    {"name": "AB de Villiers", "name_hi": "एबी डिविलियर्स", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "South Africa",
     "current_team": "-", "teams_history": ["DC", "RCB"], "jersey_no": "17",
     "ipl_stats": {"matches": 184, "runs": 5162, "balls": 3402, "highest_score": "133*", "avg": 39.70, "sr": 151.68, "fifties": 33, "hundreds": 3, "fours": 391, "sixes": 251, "wickets": 0, "catches": 102},
     "achievements": ["Mr. 360 - can hit any ball anywhere", "Most impactful overseas batsman in RCB history", "One of the greatest T20 batsmen ever"],
     "bio": "Mr. 360. AB de Villiers could hit any ball to any part of the ground. His partnership with Kohli at RCB was the most feared in IPL history.",
     "bio_hi": "मिस्टर 360। AB डिविलियर्स किसी भी गेंद को मैदान के किसी भी हिस्से में मार सकते थे। कोहली के साथ उनकी जोड़ी IPL की सबसे खतरनाक थी।"},
    {"name": "Sanju Samson", "name_hi": "संजू सैमसन", "role": "Wicketkeeper-Batsman", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "India",
     "current_team": "RR", "teams_history": ["RR", "DC"], "jersey_no": "9",
     "ipl_stats": {"matches": 158, "runs": 4144, "balls": 2912, "highest_score": "119", "avg": 29.18, "sr": 140.11, "fifties": 17, "hundreds": 4, "fours": 349, "sixes": 196, "wickets": 0, "catches": 80, "stumpings": 12},
     "achievements": ["RR captain", "Kerala's IPL star", "Fastest RR player to 3000 runs"],
     "bio": "Kerala's prince. Sanju Samson is one of the most naturally gifted batsmen in Indian cricket, leading RR with flair and aggression.",
     "bio_hi": "केरल का राजकुमार। संजू सैमसन भारतीय क्रिकेट के सबसे प्रतिभाशाली बल्लेबाजों में से एक हैं।"},
    {"name": "Pat Cummins", "name_hi": "पैट कमिंस", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm fast", "nationality": "Australia",
     "current_team": "SRH", "teams_history": ["KKR", "DC", "SRH"], "jersey_no": "30",
     "ipl_stats": {"matches": 41, "runs": 284, "balls": 180, "highest_score": "56*", "avg": 23.66, "sr": 157.77, "fifties": 1, "hundreds": 0, "fours": 18, "sixes": 22, "wickets": 42, "economy": 8.84, "best_bowling": "4/34", "catches": 8},
     "achievements": ["Most expensive IPL buy at the time", "Australian Test captain playing IPL", "SRH captain 2024"],
     "bio": "Australia's captain in the IPL. Pat Cummins brings the intensity of international cricket to the IPL with his pace and leadership.",
     "bio_hi": "IPL में ऑस्ट्रेलिया के कप्तान। पैट कमिंस अपनी तेज गेंदबाजी और नेतृत्व से IPL में अंतर्राष्ट्रीय तीव्रता लाते हैं।"},
    {"name": "Heinrich Klaasen", "name_hi": "हेनरिक क्लासेन", "role": "Wicketkeeper-Batsman", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "South Africa",
     "current_team": "SRH", "teams_history": ["SRH"], "jersey_no": "69",
     "ipl_stats": {"matches": 28, "runs": 1045, "balls": 588, "highest_score": "104", "avg": 40.19, "sr": 177.72, "fifties": 5, "hundreds": 1, "fours": 74, "sixes": 78, "wickets": 0, "catches": 14},
     "achievements": ["Highest SR in IPL 2024", "Most sixes by a wicketkeeper in a season", "SRH's game-changer"],
     "bio": "The new Mr. 360. Heinrich Klaasen's explosive batting in 2024 set new benchmarks for power-hitting from the middle order.",
     "bio_hi": "नए मिस्टर 360। हेनरिक क्लासेन की 2024 में विस्फोटक बल्लेबाजी ने मिडल ऑर्डर पावर-हिटिंग के नए मानदंड स्थापित किए।"},
    {"name": "Ruturaj Gaikwad", "name_hi": "ऋतुराज गायकवाड", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "Right-arm leg-break", "nationality": "India",
     "current_team": "CSK", "teams_history": ["CSK"], "jersey_no": "31",
     "ipl_stats": {"matches": 62, "runs": 2208, "balls": 1640, "highest_score": "108*", "avg": 37.42, "sr": 135.37, "fifties": 15, "hundreds": 2, "fours": 216, "sixes": 72, "wickets": 0, "catches": 26},
     "achievements": ["Orange Cap 2021", "CSK's new captain (post-Dhoni)", "Youngest CSK century-maker"],
     "bio": "Dhoni's heir. Ruturaj Gaikwad is the future of CSK, handpicked by Thala himself to carry forward the yellow legacy.",
     "bio_hi": "धोनी के उत्तराधिकारी। ऋतुराज गायकवाड CSK का भविष्य हैं, खुद थाला ने उन्हें पीली विरासत आगे बढ़ाने के लिए चुना।"},
]

# ==================== IPL RECORDS DATABASE ====================
IPL_RECORDS = [
    {"category": "batting", "title": "Most Runs (All-time)", "value": "8,004", "holder": "Virat Kohli", "team": "RCB", "year": "2008-present", "icon": "bat", "color": "#FF3B3B"},
    {"category": "batting", "title": "Highest Individual Score", "value": "175*", "holder": "Chris Gayle", "team": "RCB", "year": "2013 vs PWI", "icon": "flame", "color": "#FF6B6B"},
    {"category": "batting", "title": "Most Runs in a Season", "value": "973", "holder": "Virat Kohli", "team": "RCB", "year": "2016", "icon": "crown", "color": "#FFD700"},
    {"category": "batting", "title": "Fastest Century", "value": "30 balls", "holder": "Chris Gayle", "team": "PBKS", "year": "2017 vs GL", "icon": "zap", "color": "#f59e0b"},
    {"category": "batting", "title": "Most Sixes (All-time)", "value": "357", "holder": "Chris Gayle", "team": "Multiple", "year": "2009-2021", "icon": "target", "color": "#818cf8"},
    {"category": "batting", "title": "Most Fours (All-time)", "value": "706", "holder": "Virat Kohli", "team": "RCB", "year": "2008-present", "icon": "chevrons-right", "color": "#60a5fa"},
    {"category": "batting", "title": "Highest Strike Rate (min 500 runs)", "value": "177.16", "holder": "Andre Russell", "team": "KKR", "year": "2014-present", "icon": "rocket", "color": "#f472b6"},
    {"category": "batting", "title": "Most Fifties", "value": "55", "holder": "Virat Kohli", "team": "RCB", "year": "2008-present", "icon": "award", "color": "#34d399"},
    {"category": "bowling", "title": "Most Wickets (All-time)", "value": "187", "holder": "Yuzvendra Chahal", "team": "Multiple", "year": "2013-present", "icon": "crosshair", "color": "#a855f7"},
    {"category": "bowling", "title": "Best Bowling Figures", "value": "6/12", "holder": "Alzarri Joseph", "team": "MI", "year": "2019 vs SRH", "icon": "flame", "color": "#ef4444"},
    {"category": "bowling", "title": "Best Economy (min 50 matches)", "value": "6.34", "holder": "Rashid Khan", "team": "GT/SRH", "year": "2017-present", "icon": "shield", "color": "#22c55e"},
    {"category": "bowling", "title": "Most Dot Balls", "value": "1800+", "holder": "Bhuvneshwar Kumar", "team": "SRH", "year": "2011-present", "icon": "circle", "color": "#06b6d4"},
    {"category": "team", "title": "Highest Team Total", "value": "287/3", "holder": "RCB vs GL", "team": "RCB", "year": "2016", "icon": "trophy", "color": "#FF3B3B"},
    {"category": "team", "title": "Lowest Team Total", "value": "49", "holder": "RCB vs KKR", "team": "RCB", "year": "2017", "icon": "alert-circle", "color": "#ef4444"},
    {"category": "team", "title": "Most Titles", "value": "5 each", "holder": "MI & CSK", "team": "MI/CSK", "year": "Multiple", "icon": "crown", "color": "#FFD700"},
    {"category": "special", "title": "Most Expensive Player", "value": "₹24.75 Cr", "holder": "Shreyas Iyer", "team": "PBKS", "year": "2025 Auction", "icon": "indian-rupee", "color": "#f59e0b"},
    {"category": "special", "title": "Most Catches (Fielder)", "value": "122", "holder": "Virat Kohli", "team": "RCB", "year": "2008-present", "icon": "hand", "color": "#10b981"},
    {"category": "special", "title": "Most Matches Played", "value": "264", "holder": "MS Dhoni", "team": "CSK", "year": "2008-present", "icon": "calendar", "color": "#6366f1"},
]

# ==================== ORANGE & PURPLE CAP WINNERS ====================
CAP_WINNERS = [
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


async def seed_ipl_data(db):
    """Seeds IPL players, records, and cap winners into MongoDB."""
    now = utc_now().isoformat()
    
    # Seed Players
    existing_players = await db.ipl_players.count_documents({})
    if existing_players < 10:
        for p in IPL_PLAYERS:
            p_doc = {**p, "created_at": now, "updated_at": now}
            await db.ipl_players.update_one(
                {"name": p["name"]},
                {"$set": p_doc},
                upsert=True
            )
        await db.ipl_players.create_index("name")
        await db.ipl_players.create_index("current_team")
        await db.ipl_players.create_index("role")
    
    # Seed Records
    existing_records = await db.ipl_records.count_documents({})
    if existing_records < 5:
        for r in IPL_RECORDS:
            r_doc = {**r, "created_at": now}
            await db.ipl_records.update_one(
                {"title": r["title"]},
                {"$set": r_doc},
                upsert=True
            )
    
    # Seed Cap Winners
    existing_caps = await db.ipl_caps.count_documents({})
    if existing_caps < 3:
        for c in CAP_WINNERS:
            await db.ipl_caps.update_one(
                {"year": c["year"]},
                {"$set": {**c, "created_at": now}},
                upsert=True
            )
    
    players_count = await db.ipl_players.count_documents({})
    records_count = await db.ipl_records.count_documents({})
    caps_count = await db.ipl_caps.count_documents({})
    
    return {
        "players": players_count,
        "records": records_count,
        "cap_winners": caps_count
    }
