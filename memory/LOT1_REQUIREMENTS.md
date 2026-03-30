# LOT 1 — Feature Requirements + API Docs
## Date: 2026-03-30

## FEATURE REQUIREMENTS (User's Exact Words)

### Step 1: Question Pool (Max 200)
Mai maximum 200 sawal add kr dunga. Har sawal ke points bi.

### Step 2: Template System
In 200 sawal se mai kitna bi template bna skta har template me maximum 11 sawal.
Har template ka type ya toh full match ya in match with overs range specification and inning specification.
Like in_match 1-12 overs first innings, in match 12.1-20 overs first innings etc

### Step 3: Match Template Rules (Max 5 per match)
Kisi bi match me max 5 template use ho skte. 1 full match aur 4 in match. Lekin minimum 1 - Full match.

**Full match ke questions**: aap 1st innings ke 12 overs ke end tk answer kr skte. Aur kabi bi edit bi kr skte answers.

**In match answer deadlines**:
- 2nd inning 1-12 tk ka answer kr skte 2nd inning ke 5th over tk
- 2nd innings 12.1-20 tk answer kr skte 2nd innings ke 14.6 over tk
- 1st inning 1-12 tk ka answer kr skte 1st inning ke 5th over tk
- 1st innings 12.1-20 tk answer kr skte 1st innings ke 14.6 over tk

### Step 4: Auto Match Engine
Next match automatic live ho jayega. Backend me jagah hoga live ya future match me template active krne ka from already built templates.
Agar kisi match me maine nahi chuna toh jo template last match me use hua tha wo automatic use hoga.

### Step 5: Auto Answer Engine
Har ball ke baad live questions ka answer automatic scorecard se fetch krke backend ai agent answer krega.

### Step 6: Leaderboard System
User ka leaderboard rhega beautiful like dream 11 points ke aadhar pr.
Backend right answers automatic dega sare sawalo ka aur fir right answers se user ka answer match krega result ke liye.
Important: har user ke liye alag se nahi api fetch krega balki ek hi jagah backend sara right answer dekar usse user ko result dega.

### Additional Requirements
- AI-powered question generation
- Push notifications (match start, results)
- Socket.IO real-time leaderboard updates
- "Share Results on WhatsApp" feature - user apna rank + score share karega. Beautiful aesthetic card
- Animation dalo har jagah scorecard wickets runs sixes fours har jagah prize winner har jagah beautiful animations sixes lage toh screen pr bda sa aaye 6 ka sign etc
- Sabhi contest kisi match ke us match ke start time se 24 hours phle live ho jayenge

---

## LOT 1 — API DOCUMENTATION (Raw Payloads)

### API 1: Current Matches
**Endpoint**: `GET /v1/currentMatches?apikey={key}&offset=0`
**URL**: `https://api.cricapi.com/v1/currentMatches`
**Purpose**: Get currently active/recent matches

**Sample Response Structure**:
```json
{
  "data": [
    {
      "id": "e02475c1-8f9a-4915-a9e8-d4dbc3441c96",
      "name": "Mumbai Indians vs Kolkata Knight Riders, 2nd Match, Indian Premier League 2026",
      "matchType": "t20",
      "status": "Mumbai Indians won by 6 wkts",
      "venue": "Wankhede Stadium, Mumbai",
      "date": "2026-03-29",
      "dateTimeGMT": "2026-03-29T14:00:00",
      "teams": ["Mumbai Indians", "Kolkata Knight Riders"],
      "teamInfo": [
        {
          "name": "Kolkata Knight Riders",
          "shortname": "KKR",
          "img": "https://g.cricapi.com/iapi/206-637852958714346149.png?w=48"
        },
        {
          "name": "Mumbai Indians",
          "shortname": "MI",
          "img": "https://g.cricapi.com/iapi/226-637852956375593901.png?w=48"
        }
      ],
      "score": [
        {"r": 220, "w": 4, "o": 20, "inning": "Kolkata Knight Riders Inning 1"},
        {"r": 224, "w": 4, "o": 19.1, "inning": "Mumbai Indians Inning 1"}
      ],
      "series_id": "87c62aac-bc3c-4738-ab93-19da0690488f",
      "fantasyEnabled": true,
      "bbbEnabled": false,
      "hasSquad": true,
      "matchStarted": true,
      "matchEnded": true
    }
  ],
  "status": "success",
  "info": {
    "hitsToday": 6,
    "hitsUsed": 1,
    "hitsLimit": 2000
  }
}
```

**Key IPL Matches Found (IPL 2026 series_id: 87c62aac-bc3c-4738-ab93-19da0690488f)**:
- RCB vs SRH (1st Match) — RCB won by 6 wkts | Score: SRH 201/9(20) vs RCB 203/4(15.4)
- MI vs KKR (2nd Match) — MI won by 6 wkts | Score: KKR 220/4(20) vs MI 224/4(19.1)

### API 2: eCricScore (Live Scores - Lightweight)
**Endpoint**: `GET /v1/cricScore?apikey={key}`
**URL**: `https://api.cricapi.com/v1/cricScore`
**Purpose**: Lightweight live score feed (no API hit count impact noted)

**Sample Response Structure**:
```json
{
  "data": [
    {
      "id": "e92727d0-61fc-4c6f-82ed-cde4789745a2",
      "dateTimeGMT": "2026-04-05T14:00:00",
      "matchType": "t20",
      "status": "Match starts at Apr 05, 14:00 GMT",
      "ms": "fixture",
      "t1": "Chennai Super Kings [CSK]",
      "t2": "Royal Challengers Bengaluru [RCBW]",
      "t1s": "",
      "t2s": "",
      "t1img": "https://g.cricapi.com/iapi/135-637852956181378533.png?w=48",
      "t2img": "https://g.cricapi.com/iapi/21439-638468478038395955.jpg?w=48",
      "series": "Indian Premier League 2026"
    },
    {
      "id": "e02475c1-...",
      "ms": "result",
      "t1": "Kolkata Knight Riders [KKR]",
      "t2": "Mumbai Indians [MI]",
      "t1s": "220/4 (20)",
      "t2s": "224/4 (19.1)",
      "status": "Mumbai Indians won by 6 wkts",
      "series": "Indian Premier League 2026"
    }
  ]
}
```
**ms field values**: "fixture" (upcoming), "result" (completed), "live" (in progress)

### API 3: Series Search
**Endpoint**: `GET /v1/series?apikey={key}&offset=0&search={query}`
**URL**: `https://api.cricapi.com/v1/series`
**Purpose**: Search/list all cricket series

**Sample Response Structure**:
```json
{
  "data": [
    {
      "id": "87c62aac-bc3c-4738-ab93-19da0690488f",
      "name": "Indian Premier League 2026",
      "startDate": "2026-03-28",
      "endDate": "May 25",
      "odi": 0,
      "t20": 74,
      "test": 0,
      "squads": 10,
      "matches": 74
    }
  ],
  "info": {
    "totalRows": 1004
  }
}
```

---

## IMPORTANT NOTES
- IPL 2026 Series ID: `87c62aac-bc3c-4738-ab93-19da0690488f`
- API Key: `8397379b-fa88-4c9d-937f-c59bcade6576`
- Rate Limit: 2000 hits/day
- cricScore API gives lightweight scores with `ms` field (fixture/result/live)
- currentMatches gives full score arrays with r/w/o per innings
- Team images available via `teamInfo[].img` URLs
