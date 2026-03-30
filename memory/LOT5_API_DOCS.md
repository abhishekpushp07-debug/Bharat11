# LOT 5 — Final API Documentation (Player Info, Fantasy Squad, Series Squads, Fantasy Scorecard)
## Date: 2026-03-30

---

## API 1: Player Info (Detailed)
**Endpoint**: `GET /v1/players_info?apikey={key}&id={player_id}`
**URL**: `https://api.cricapi.com/v1/players_info`
**Purpose**: Full player profile — role, batting/bowling style, career stats across formats
**Response Size**: ~10KB | **Response Time**: ~470ms
**Tag**: "new changes"

**Sample Player**: Srishti Raha (id: fe07f9f3-69e4-4526-aae4-67f8285aabc6)

**Response Structure**:
```json
{
  "data": {
    "id": "fe07f9f3-69e4-4526-aae4-67f8285aabc6",
    "name": "Srishti Raha",
    "role": "WK-Batsman",
    "battingStyle": "Right Handed Bat",
    "placeOfBirth": "--",
    "country": "Canada",
    "playerImg": "https://h.cricapi.com/img/icon512.png",
    "stats": [
      {
        "fn": "batting",
        "matchtype": "test",
        "stat": " m ",
        "value": " 0 "
      },
      {
        "fn": "batting",
        "matchtype": "t20",
        "stat": " runs ",
        "value": " 0 "
      },
      {
        "fn": "bowling",
        "matchtype": "odi",
        "stat": " wkts ",
        "value": " 0 "
      }
    ]
  },
  "info": {"hitsUsed": 1, "queryTime": 186.4382}
}
```

### Key Player Fields:
| Field | Type | Description |
|-------|------|-------------|
| id | string | Player UUID |
| name | string | Full name |
| role | string | WK-Batsman, Batsman, Bowler, Batting Allrounder, Bowling Allrounder, -- |
| battingStyle | string | "Right Handed Bat" / "Left Handed Bat" |
| bowlingStyle | string | "Right-arm fast", "Left-arm orthodox", etc. (optional) |
| placeOfBirth | string | City or "--" |
| country | string | Country name |
| playerImg | string | Player image URL (default icon if no photo) |

### Stats Array Structure:
| Field | Values | Description |
|-------|--------|-------------|
| fn | "batting" / "bowling" | Function type |
| matchtype | "test" / "odi" / "t20" | Format |
| stat | "m", "inn", "runs", "bf", "hs", "avg", "sr", "no", "4s", "6s", "50", "100", "200" (batting) | Stat name |
| stat | "m", "inn", "b", "runs", "wkts", "avg", "econ", "sr", "bbi", "bbm", "5w", "10w" (bowling) | Stat name |
| value | string | Stat value (needs trimming) |

**NOTE**: Stats values have leading/trailing spaces — must `.trim()` before parsing.

---

## API 2: Fantasy Squad (Match-level)
**Endpoint**: `GET /v1/match_squad?apikey={key}&id={match_id}`
**URL**: `https://api.cricapi.com/v1/match_squad`
**Purpose**: Playing squad for a specific match — both teams with full player details
**Response Size**: ~9KB | **Response Time**: ~379ms
**Tag**: "new changes" (listed as "Fantasy Squad" in CricketData UI)

**Sample Match**: Hobart Hurricanes Women vs Sydney Thunder Women (id: ea479cff-ddbe-48e0-9e4a-528f61a8a175)

**Response Structure**:
```json
{
  "data": [
    {
      "teamName": "Hobart Hurricanes Women",
      "shortname": "HB-W",
      "img": "https://g.cricapi.com/iapi/2635-638040172943294988.webp?w=48",
      "players": [
        {
          "id": "1015f62e-be4e-4388-9e8f-1f262b7dcc88",
          "name": "Ruth Johnston",
          "role": "Batsman",
          "battingStyle": "Right Handed Bat",
          "bowlingStyle": "Right-arm medium",
          "country": "Australia",
          "playerImg": "https://h.cricapi.com/img/icon512.png"
        },
        {
          "id": "35c2276c-1c8f-48fe-88cb-7b80561b5fba",
          "name": "Lizelle Lee",
          "role": "WK-Batsman",
          "battingStyle": "Right Handed Bat",
          "bowlingStyle": "Right-arm medium",
          "country": "South Africa",
          "playerImg": "https://h.cricapi.com/img/players/35c2276c-1c8f-48fe-88cb-7b80561b5fba.jpg"
        }
      ]
    },
    {
      "teamName": "Sydney Thunder Women",
      "shortname": "ST-W",
      "img": "https://g.cricapi.com/iapi/2636-...",
      "players": [...]
    }
  ],
  "info": {"hitsUsed": 1, "queryTime": 18.3362}
}
```

### Key Squad Fields:
| Field | Type | Description |
|-------|------|-------------|
| teamName | string | Full team name |
| shortname | string | Short code (HB-W, ST-W) |
| img | string | Team logo URL |
| players[] | array | Array of player objects |
| player.id | string | Player UUID (matches scorecard/points IDs) |
| player.name | string | Full name |
| player.role | string | WK-Batsman, Batsman, Bowler, Batting Allrounder, Bowling Allrounder, -- |
| player.battingStyle | string | Batting style |
| player.bowlingStyle | string | Bowling style (optional — not all players have it) |
| player.country | string | Country |
| player.playerImg | string | Player photo URL |

**KEY INSIGHT**: Player IDs in squad match EXACTLY with scorecard/points APIs — critical for cross-referencing!

---

## API 3: Series Squads (All Teams in a Series)
**Endpoint**: `GET /v1/series_squad?apikey={key}&id={series_id}`
**URL**: `https://api.cricapi.com/v1/series_squad`
**Purpose**: All team squads for an entire series — every team + every player
**Response Size**: ~53KB | **Response Time**: ~965ms (LARGE!)
**Tag**: ⭐ Premium

**Sample Series**: Pakistan Super League 2026 (id: 8bfedb5a-500c-4f02-a5c3-17a3d731fe9c)

**Response Structure**:
```json
{
  "data": [
    {
      "teamName": "Islamabad United",
      "shortname": "ISU",
      "img": "https://g.cricapi.com/iapi/34-637992689284766336.webp?w=48",
      "players": [
        {
          "id": "26c7e157-99e8-46b3-9675-5350e8e79270",
          "name": "Shadab Khan",
          "role": "Bowling Allrounder",
          "battingStyle": "Right Handed Bat",
          "bowlingStyle": "Right-arm legbreak",
          "country": "Pakistan",
          "playerImg": "https://h.cricapi.com/img/players/26c7e157-..jpg"
        }
      ]
    },
    {"teamName": "Karachi Kings", "players": [...]},
    {"teamName": "Lahore Qalandars", "players": [...]},
    {"teamName": "Peshawar Zalmi", "players": [...]},
    {"teamName": "Quetta Gladiators", "players": [...]},
    {"teamName": "Hyderabad Kingsmen", "players": [...]},
    {"teamName": "Rawalpindiz", "players": [...]},
    {"teamName": "Multan Sultans", "players": [...]}
  ],
  "info": {"hitsUsed": 1, "queryTime": 301.6916}
}
```

### PSL 2026 Teams Found (8 teams):
| Team | Shortname | Notable Players |
|------|-----------|-----------------|
| Islamabad United | ISU | Shadab Khan, Devon Conway, Imad Wasim |
| Karachi Kings | KRK | David Warner, Moeen Ali, Adam Zampa, Hasan Ali |
| Lahore Qalandars | LHQ | Shaheen Afridi, Fakhar Zaman, Haris Rauf, Mustafizur Rahman |
| Peshawar Zalmi | PSZ | Babar Azam, Kusal Mendis, Aaron Hardie |
| Quetta Gladiators | QTG | Rilee Rossouw, Alzarri Joseph, Tom Curran, Saud Shakeel |
| Hyderabad Kingsmen | HK | Saim Ayub, Marnus Labuschagne, Kusal Perera |
| Rawalpindiz | R | Mohammad Rizwan, Naseem Shah, Mohammad Amir, Usman Khawaja |
| Multan Sultans | MS | Steven Smith, Shan Masood, Tabraiz Shamsi |

### Player Roles Found:
- Batsman, Bowler, WK-Batsman, Batting Allrounder, Bowling Allrounder, -- (unknown)

**KEY INSIGHTS**:
- 53KB response — CACHE THIS! Only call once per series
- ~20 players per team, ~160 players total for PSL
- IPL will have ~10 teams * ~25 players = ~250 players
- Some players have no `role` or `bowlingStyle` — handle gracefully

---

## API 4: Fantasy Scorecard (RE-CONFIRMATION)
**Endpoint**: `GET /v1/match_scorecard?apikey={key}&id={match_id}`
**Note**: This is the SAME as LOT 3's Match Scorecard API. User re-sent for completeness.
**Already documented in**: `/app/memory/LOT3_API_DOCS.md`
**Status**: ✅ No new data — identical to LOT 3 payload.

---

## FINAL CUMULATIVE API STATUS (ALL 5 LOTS COMPLETE)

| # | API | Endpoint | LOT | Priority | Status |
|---|-----|----------|-----|----------|--------|
| 1 | Current Matches | `/v1/currentMatches` | LOT 1 | CRITICAL | ✅ Documented |
| 2 | eCricScore | `/v1/cricScore` | LOT 1 | HIGH | ✅ Documented |
| 3 | Series Search | `/v1/series?search=` | LOT 1 | MEDIUM | ✅ Documented |
| 4 | Series List | `/v1/series?offset=` | LOT 2+3 | LOW | ✅ Documented |
| 5 | Matches List | `/v1/matches?offset=` | LOT 2 | LOW | ✅ Documented |
| 6 | Players List/Search | `/v1/players` | LOT 2 | LOW | ✅ Documented |
| 7 | Series Info | `/v1/series_info?id=` | LOT 2 | HIGH | ✅ Documented |
| 8 | Match Info | `/v1/match_info?id=` | LOT 2 | HIGH | ✅ Documented |
| 9 | Player Info | `/v1/players_info?id=` | LOT 5 | LOW | ✅ Documented |
| 10 | Match Scorecard | `/v1/match_scorecard?id=` | LOT 3+5 | CRITICAL | ✅ Documented |
| 11 | Fantasy Match Points | `/v1/match_points?id=` | LOT 3 | MEDIUM | ✅ Documented |
| 12 | Series Points Table | `/v1/series_points?id=` | LOT 3 | LOW | ✅ Documented |
| 13 | Ball-by-Ball | `/v1/match_bbb?id=` | LOT 4 | LOW | ✅ Documented (IN TESTING) |
| 14 | Fantasy Squad (Match) | `/v1/match_squad?id=` | LOT 5 | MEDIUM | ✅ Documented |
| 15 | Series Squads | `/v1/series_squad?id=` | LOT 5 | MEDIUM | ✅ Documented |
| 16 | Fantasy XI | `/v1/fantasy_xi?id=` | LOT 2 | SKIP | DO NOT USE |
| 17 | Country List | `/v1/countries` | — | VERY LOW | Not needed |

### DOCUMENTATION COMPLETE: 15/15 usable APIs documented! ✅

---

## API BUDGET STRATEGY (2000 hits/day)

### Per-Match Cost (Estimated):
| Action | API | Hits | When |
|--------|-----|------|------|
| Detect live matches | cricScore | 1 | Every 45s polling |
| Get match details | match_info | 1 | Once per match |
| Get scorecard | match_scorecard | 1 | Every poll cycle |
| Get squad | match_squad | 1 | Once per match |
| Total per poll | — | ~2 | Every 45s |

### Daily Budget (2000 hits):
- Polling 45s = 80 polls/hour = 1920/day (24h)
- **Realistic**: Only poll during match hours (~8h/day) = 640 polls
- Each poll = 2-3 API calls = ~1920 calls/day (fits in budget!)
- Series squad/info: Call ONCE, cache for entire series

### Caching Strategy:
- `series_info` → Cache 24h (schedule doesn't change often)
- `series_squad` → Cache 24h (squads rarely change mid-series)
- `match_squad` → Cache per match (one-time)
- `match_scorecard` → NO CACHE during live (changes every ball)
- `cricScore` → NO CACHE (real-time polling)
- `match_points` → Cache 5min (2s response, expensive)
