# LOT 4 — Ball-by-Ball API + Requirements Re-confirmation
## Date: 2026-03-30

---

## API 1: Fantasy Ball-by-Ball (BBB)
**Endpoint**: `GET /v1/match_bbb?apikey={key}&id={match_id}`
**URL**: `https://api.cricapi.com/v1/match_bbb`
**Purpose**: Ball-by-ball delivery data — every extras/penalty event in the match
**Status**: IN TESTING (as per CricketData.org)
**Response Size**: ~10KB | **Response Time**: ~230ms

**Sample Match**: Hobart Hurricanes Women vs Sydney Thunder Women (id: ea479cff-ddbe-48e0-9e4a-528f61a8a175)

**Response Structure**:
```json
{
  "data": {
    "id": "ea479cff-ddbe-48e0-9e4a-528f61a8a175",
    "name": "Hobart Hurricanes Women vs Sydney Thunder Women, 6th Match",
    "matchType": "t20",
    "status": "Hobart Hurricanes Women won by 5 wkts",
    "teams": ["Hobart Hurricanes Women", "Sydney Thunder Women"],
    "teamInfo": [...],
    "tossWinner": "hobart hurricanes women",
    "tossChoice": "bowl",
    "matchWinner": "Hobart Hurricanes Women",
    "series_id": "f6f07506-8226-4882-8b03-fadb1e696826",
    "bbb": [
      {
        "n": 1,
        "inning": 0,
        "over": 1,
        "ball": 3,
        "batsman": {"id": "09c3e5a8-...", "name": "Olivia Maxwell"},
        "bowler": {"id": "19541736-...", "name": "Molly Strano"},
        "runs": 0,
        "penalty": "wide",
        "extras": 1
      },
      {
        "n": 10,
        "inning": 0,
        "over": 7,
        "ball": 4,
        "batsman": {"id": "2953dbeb-...", "name": "Hasrat Gill"},
        "bowler": {"id": "43fed1ec-...", "name": "Lauren Smith"},
        "runs": 0,
        "penalty": "byes",
        "extras": 1
      },
      {
        "n": 13,
        "inning": 1,
        "over": 1,
        "ball": 1,
        "batsman": {"id": "35c2276c-...", "name": "Lizelle Lee"},
        "bowler": {"id": "212c3e90-...", "name": "Samantha Bates"},
        "runs": 0,
        "penalty": "wide",
        "extras": 3
      }
    ],
    "matchStarted": true,
    "matchEnded": true
  },
  "info": {"hitsUsed": 1, "queryTime": 26.2203}
}
```

### Key BBB Fields:
| Field | Type | Description |
|-------|------|-------------|
| n | int | Sequential ball number (global across match) |
| inning | int | 0 = 1st innings, 1 = 2nd innings |
| over | int | Over number (1-indexed) |
| ball | int | Ball number within the over |
| batsman.id | string | Batsman UUID |
| batsman.name | string | Batsman name |
| bowler.id | string | Bowler UUID |
| bowler.name | string | Bowler name |
| runs | int | Runs off bat |
| penalty | string | "wide", "byes", "noball", "legbyes" etc. |
| extras | int | Extra runs |

### CRITICAL OBSERVATIONS:
1. **BBB is IN TESTING** — data may be incomplete/unreliable
2. **Only shows extras/penalties** — regular deliveries (dot, 1, 2, 4, 6) are NOT in this sample
3. **Inning field**: 0-indexed (0 = 1st innings, 1 = 2nd innings) — DIFFERENT from scorecard which uses text
4. **Over tracking**: `over` + `ball` gives exact delivery position (e.g., over=6, ball=4 = 6.4 overs)
5. **This API is KEY for auto-answer deadline tracking** — can detect "5th over completed" or "14.6 overs done"
6. **But unreliable**: Only extras shown, not every delivery. May not be usable for production deadline tracking.

### USE CASE for Bharat 11:
- Could be used to track current over progress for in-match template deadlines
- BUT since it's "in testing" and only shows extras, better to rely on `scorecard` API's `o` field (overs bowled) for deadline enforcement
- `score[].o` field from `currentMatches` or `match_info` gives current over count reliably

---

## REQUIREMENTS RE-CONFIRMATION (User's Exact Words — Message 2)

User re-pasted the FULL requirements. Cross-checking with LOT1_REQUIREMENTS.md:

### Verified Match (LOT 1 vs This Message):
- ✅ Step 1: 200 question pool with points — MATCH
- ✅ Step 2: Templates from question pool, max 11 per template, type: full_match / in_match with over+inning spec — MATCH
- ✅ Step 3: Max 5 templates per match (1 full + 4 in-match), deadline rules — MATCH
- ✅ Step 4: Auto match engine, template inheritance — MATCH
- ✅ Step 5: Auto answer from scorecard per ball — MATCH
- ✅ Step 6: Leaderboard, single backend answer source — MATCH
- ✅ AI-powered question generation — MATCH
- ✅ Push notifications — MATCH
- ✅ Socket.IO real-time leaderboard — MATCH
- ✅ WhatsApp share with aesthetic card — MATCH
- ✅ Heavy animations (sixes, wickets, prizes) — MATCH
- ✅ 24 hours before match start = contest goes live — MATCH

### NEW/CLARIFIED from this message:
- "Premium me limit hai 2000 per day api call ka cricket data se. Apna limit bdhao aur pta kro mai shi bol rha ya nahi" — User confirming 2000/day limit on premium plan ✅
- "Ek betting app banana hai new type ka" — Confirms this is a BETTING app, not just fantasy prediction

**CONCLUSION**: All requirements in LOT 1 are accurate and complete. No new requirements added.

---

## SCREENSHOT COMPARISON — CricketData.org API List vs Our Documentation

### From Screenshot (cricketdata.org/member-test.aspx):

**List APIs:**
| API | In Screenshot | Documented? | LOT |
|-----|--------------|-------------|-----|
| Current Matches | ✅ Top Used | ✅ | LOT 1 |
| eCricScore | ✅ Top Used | ✅ | LOT 1 |
| Series Search | ✅ new changes | ✅ | LOT 1 |
| Series List | ✅ | ✅ | LOT 2+3 |
| Matches List | ✅ | ✅ | LOT 2 |
| Players List | ✅ | ✅ | LOT 2 |
| Players Search | ✅ | ✅ | LOT 2 |

**Cricket Info APIs:**
| API | In Screenshot | Documented? | LOT |
|-----|--------------|-------------|-----|
| Series Info | ✅ | ✅ | LOT 2 |
| Match Info | ✅ | ✅ | LOT 2 |
| Player Info | ✅ new changes | ❌ MISSING | — |

**Fantasy APIs:**
| API | In Screenshot | Documented? | LOT |
|-----|--------------|-------------|-----|
| Fantasy Squad | ✅ new changes | ❌ MISSING | — |
| Series Squads | ✅ ⭐ | ❌ MISSING | — |
| Fantasy Scorecard | ✅ ⭐ | ❌ MISSING | — |
| Fantasy Match Points | ✅ ⭐ | ✅ | LOT 3 |
| Series Point Table | ✅ ⭐ | ✅ | LOT 3 |
| Fantasy XI | ✅ DO NOT USE | ✅ (noted) | LOT 2 |
| Fantasy Ball-by-Ball | ✅ in testing | ✅ | LOT 4 |

**Misc APIs:**
| API | In Screenshot | Documented? | LOT |
|-----|--------------|-------------|-----|
| Country List | ✅ | ❌ MISSING | — |

**Coming Soon:**
| API | Status |
|-----|--------|
| Custom Banner | coming soon |

### MISSING APIs (Need LOT 5):
1. **Player Info** (`/v1/player_info?id=`) — marked "new changes" — NEED PAYLOAD
2. **Fantasy Squad** (`/v1/fantasy_squad?id=`) — marked "new changes" — NEED PAYLOAD
3. **Series Squads** (`/v1/series_squad?id=`) — marked ⭐ — NEED PAYLOAD
4. **Fantasy Scorecard** (`/v1/fantasy_scorecard?id=`) — marked ⭐ — NEED PAYLOAD
5. **Country List** (`/v1/countries`) — low priority

### ALSO ALREADY IMPLEMENTED (not in screenshot list but in codebase):
- **Match Scorecard** (`/v1/match_scorecard`) — Already in LOT 3 + already implemented in backend

---

## CUMULATIVE API STATUS (All 4 LOTs)

| # | API | Endpoint | Documented | Priority for Bharat 11 |
|---|-----|----------|-----------|----------------------|
| 1 | Current Matches | `/v1/currentMatches` | ✅ LOT 1 | HIGH — match detection |
| 2 | eCricScore | `/v1/cricScore` | ✅ LOT 1 | HIGH — lightweight polling |
| 3 | Series Search | `/v1/series?search=` | ✅ LOT 1 | MEDIUM |
| 4 | Series List | `/v1/series?offset=` | ✅ LOT 2+3 | LOW |
| 5 | Matches List | `/v1/matches?offset=` | ✅ LOT 2 | LOW |
| 6 | Players List/Search | `/v1/players` | ✅ LOT 2 | LOW |
| 7 | Series Info | `/v1/series_info?id=` | ✅ LOT 2 | HIGH — full schedule |
| 8 | Match Info | `/v1/match_info?id=` | ✅ LOT 2 | HIGH — toss, winner |
| 9 | Match Scorecard | `/v1/match_scorecard?id=` | ✅ LOT 3 | CRITICAL — auto-answer |
| 10 | Fantasy Match Points | `/v1/match_points?id=` | ✅ LOT 3 | MEDIUM |
| 11 | Series Points Table | `/v1/series_points?id=` | ✅ LOT 3 | LOW |
| 12 | Ball-by-Ball | `/v1/match_bbb?id=` | ✅ LOT 4 | LOW (in testing) |
| 13 | Player Info | `/v1/player_info?id=` | ❌ MISSING | LOW |
| 14 | Fantasy Squad | `/v1/fantasy_squad?id=` | ❌ MISSING | MEDIUM |
| 15 | Series Squads | `/v1/series_squad?id=` | ❌ MISSING | MEDIUM |
| 16 | Fantasy Scorecard | `/v1/fantasy_scorecard?id=` | ❌ MISSING | MEDIUM |
| 17 | Country List | `/v1/countries` | ❌ MISSING | VERY LOW |
