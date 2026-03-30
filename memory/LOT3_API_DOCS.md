# LOT 3 — API Documentation (Raw Payloads)
## Date: 2026-03-30

---

## API 1: Match Scorecard (Full Detail)
**Endpoint**: `GET /v1/match_scorecard?apikey={key}&id={match_id}`
**URL**: `https://api.cricapi.com/v1/match_scorecard`
**Purpose**: Full detailed scorecard — batting, bowling, catching, extras per innings
**Response Size**: ~20KB | **Response Time**: ~289ms

**Sample Match**: Hobart Hurricanes Women vs Sydney Thunder Women (id: ea479cff-ddbe-48e0-9e4a-528f61a8a175)

**Sample Response**:
```json
{
  "data": {
    "id": "ea479cff-ddbe-48e0-9e4a-528f61a8a175",
    "name": "Hobart Hurricanes Women vs Sydney Thunder Women, 6th Match",
    "matchType": "t20",
    "status": "Hobart Hurricanes Women won by 5 wkts",
    "venue": "Cricket Central, Sydney",
    "date": "2025-10-22",
    "dateTimeGMT": "2025-10-22T03:30:00",
    "teams": ["Hobart Hurricanes Women", "Sydney Thunder Women"],
    "teamInfo": [
      {"name": "Hobart Hurricanes Women", "shortname": "HB-W", "img": "https://g.cricapi.com/iapi/2635-638040172943294988.webp?w=48"},
      {"name": "Sydney Thunder Women", "shortname": "ST-W", "img": "https://g.cricapi.com/iapi/2636-638040169751591741.webp?w=48"}
    ],
    "score": [
      {"r": 92, "w": 10, "o": 17.4, "inning": "Sydney Thunder Women Inning 1"},
      {"r": 95, "w": 5, "o": 16, "inning": "Hobart Hurricanes Women Inning 1"}
    ],
    "tossWinner": "hobart hurricanes women",
    "tossChoice": "bowl",
    "matchWinner": "Hobart Hurricanes Women",
    "series_id": "f6f07506-8226-4882-8b03-fadb1e696826",
    "scorecard": [
      {
        "inning": "Sydney Thunder Women Inning 1",
        "batting": [
          {
            "batsman": {"id": "723ea4eb-...", "name": "Tahlia Wilson"},
            "dismissal": "catch",
            "bowler": {"id": "f661fa24-...", "name": "Nicola Carey"},
            "catcher": {"id": "35c2276c-...", "name": "Lizelle Lee"},
            "dismissal-text": "c lizelle lee b nicola carey",
            "r": 1, "b": 3, "4s": 0, "6s": 0, "sr": 33.33
          }
        ],
        "bowling": [
          {
            "bowler": {"id": "f661fa24-...", "name": "Nicola Carey"},
            "o": 4, "m": 0, "r": 20, "w": 2, "nb": 0, "wd": 1, "eco": 5
          },
          {
            "bowler": {"id": "19541736-...", "name": "Molly Strano"},
            "o": 4, "m": 1, "r": 9, "w": 4, "nb": 0, "wd": 2, "eco": 2.2
          }
        ],
        "catching": [
          {
            "catcher": {"id": "35c2276c-...", "name": "Lizelle Lee"},
            "stumped": 0, "runout": 0, "catch": 2, "cb": 0, "lbw": 0, "bowled": 0
          }
        ],
        "extras": {"r": 11, "b": 1},
        "totals": {}
      }
    ],
    "matchStarted": true,
    "matchEnded": true
  },
  "status": "success",
  "info": {"hitsToday": 42, "hitsUsed": 1, "hitsLimit": 2000}
}
```

### Key Data Fields — Batting:
| Field | Type | Description |
|-------|------|-------------|
| batsman.id | string | Player UUID |
| batsman.name | string | Player name |
| dismissal | string | catch/bowled/lbw/cb/stumped/runout |
| bowler.id/name | string | Who dismissed |
| catcher.id/name | string | Catcher (if catch) |
| dismissal-text | string | Full text "c X b Y" |
| r | int | Runs scored |
| b | int | Balls faced |
| 4s | int | Fours |
| 6s | int | Sixes |
| sr | float | Strike rate |

### Key Data Fields — Bowling:
| Field | Type | Description |
|-------|------|-------------|
| bowler.id | string | Player UUID |
| bowler.name | string | Player name |
| o | float | Overs bowled |
| m | int | Maidens |
| r | int | Runs conceded |
| w | int | Wickets |
| nb | int | No balls |
| wd | int | Wides |
| eco | float | Economy rate |

### Key Data Fields — Catching:
| Field | Type | Description |
|-------|------|-------------|
| catcher.id | string | Player UUID |
| stumped | int | Stumpings |
| runout | int | Run outs |
| catch | int | Catches |
| cb | int | Caught & bowled |
| lbw | int | LBW |
| bowled | int | Bowled |

### Key Data Fields — Extras:
| Field | Type | Description |
|-------|------|-------------|
| r | int | Total extra runs |
| b | int | Byes |

---

## API 2: Fantasy Match Points
**Endpoint**: `GET /v1/match_points?apikey={key}&id={match_id}&ruleset=0`
**URL**: `https://api.cricapi.com/v1/match_points`
**Purpose**: Fantasy points per player — broken down by innings (batting, bowling, catching) + total
**Response Size**: ~10KB | **Response Time**: ~2243ms (SLOW!)
**Note**: `ruleset=0` is default ruleset

**Sample Match**: Hobart Hurricanes Women vs Sydney Thunder Women

**Response Structure**:
```json
{
  "data": {
    "innings": [
      {
        "inning": "Sydney Thunder Women Inning 1",
        "batting": [
          {"id": "723ea4eb-...", "name": "Tahlia Wilson", "points": 3},
          {"id": "09c3e5a8-...", "name": "Olivia Maxwell", "points": 38}
        ],
        "bowling": [
          {"id": "f661fa24-...", "name": "Nicola Carey", "points": 28},
          {"id": "19541736-...", "name": "Molly Strano", "points": 35}
        ],
        "catching": [
          {"id": "35c2276c-...", "name": "Lizelle Lee", "points": 47},
          {"id": "38b64c4c-...", "name": "Elyse Villani", "points": 23}
        ]
      },
      {
        "inning": "Hobart Hurricanes Women Inning 1",
        "batting": [...],
        "bowling": [...],
        "catching": [...]
      }
    ],
    "totals": [
      {"id": "35c2276c-...", "name": "Lizelle Lee", "points": 47},
      {"id": "09c3e5a8-...", "name": "Olivia Maxwell", "points": 38},
      {"id": "19541736-...", "name": "Molly Strano", "points": 35},
      {"id": "f661fa24-...", "name": "Nicola Carey", "points": 28},
      {"id": "0475753e-...", "name": "Laura Harris", "points": 24},
      {"id": "4f1f5f34-...", "name": "Taneale Peschel", "points": 24}
    ]
  },
  "info": {"hitsUsed": 1, "ruleset": 0, "queryTime": 1925.5754}
}
```

### Key Insights:
- **Points per innings**: Batting/Bowling/Catching breakdowns per inning
- **Totals**: Combined points across all innings — SORTED by highest
- **Ruleset 0**: Default fantasy scoring rules
- **SLOW API**: ~2 seconds response time — cache heavily!
- **Can negative**: Players can have negative points (e.g., -8 for Emily Powell)

---

## API 3: Series Points Table (Team Standings)
**Endpoint**: `GET /v1/series_points?apikey={key}&id={series_id}`
**URL**: `https://api.cricapi.com/v1/series_points`
**Purpose**: Team standings for a series (matches, wins, losses, ties, NR)
**Response Size**: ~3KB | **Response Time**: ~480ms

**Sample Series**: Pakistan Super League 2026 (id: 8bfedb5a-500c-4f02-a5c3-17a3d731fe9c)

**Response Structure**:
```json
{
  "data": [
    {
      "teamname": "Karachi Kings",
      "shortname": "KRK",
      "img": "https://g.cricapi.com/iapi/37-637992689033348642.webp?w=48",
      "matches": 2,
      "wins": 2,
      "loss": 0,
      "ties": 0,
      "nr": 0
    },
    {
      "teamname": "Lahore Qalandars",
      "shortname": "LHQ",
      "img": "https://g.cricapi.com/iapi/41-637991979136379824.webp?w=48",
      "matches": 2,
      "wins": 1,
      "loss": 1,
      "ties": 0,
      "nr": 0
    }
  ],
  "info": {"hitsUsed": 1, "queryTime": 36.1546}
}
```

### Key Fields:
| Field | Description |
|-------|-------------|
| teamname | Full team name |
| shortname | Short code (KRK, LHQ, etc.) |
| img | Team logo URL |
| matches | Total matches played |
| wins | Wins |
| loss | Losses |
| ties | Ties |
| nr | No Result |

---

## API 4: Series List (Full with Pagination)
**Endpoint**: `GET /v1/series?apikey={key}&offset=0`
**Purpose**: Browse ALL cricket series worldwide (1004 total rows)
**Pagination**: offset=0, 25 per page

**Key Upcoming Series (from response)**:
| Series | Start Date | Type | Matches |
|--------|-----------|------|---------|
| India tour of Ireland, 2026 | Jun 26 | T20 | 2 |
| India tour of England, 2026 | Jul 01 | ODI+T20 | 8 |
| The Hundred Men's 2026 | Jul 21 | T20 | 34 |
| Pakistan tour of England 2026 | Aug 19 | Test | 3 |
| West Indies tour of India, 2026 | Sep 27 | ODI+T20 | 8 |
| Sri Lanka tour of India, 2026 | Dec 13 | ODI+T20 | 6 |
| Australia tour of India, 2027 | Jan 21 | Test | 5 |

---

## CUMULATIVE API SUMMARY (LOT 1 + LOT 2 + LOT 3)

### APIs Already Documented:
| # | API | Endpoint | LOT | Key Use |
|---|-----|----------|-----|---------|
| 1 | Current Matches | `/v1/currentMatches` | LOT 1 | Live/recent matches with scores |
| 2 | eCricScore | `/v1/cricScore` | LOT 1 | Lightweight live scores (ms field) |
| 3 | Series Search | `/v1/series?search=` | LOT 1 | Find specific series |
| 4 | Series List | `/v1/series?offset=` | LOT 2+3 | Browse all series (1004 rows) |
| 5 | Matches List | `/v1/matches?offset=` | LOT 2 | Browse all matches (14403 rows) |
| 6 | Players List/Search | `/v1/players` | LOT 2 | Find players (18014 rows) |
| 7 | Series Info | `/v1/series_info?id=` | LOT 2 | Full series + match list |
| 8 | Match Info | `/v1/match_info?id=` | LOT 2 | Single match detail (toss, winner) |
| 9 | Match Scorecard | `/v1/match_scorecard?id=` | LOT 3 | Full batting/bowling/catching per innings |
| 10 | Fantasy Match Points | `/v1/match_points?id=` | LOT 3 | Player fantasy points per innings |
| 11 | Series Points Table | `/v1/series_points?id=` | LOT 3 | Team standings (W/L/T/NR) |

### APIs Still Pending Documentation:
| # | API | Endpoint | Status |
|---|-----|----------|--------|
| 12 | Fantasy Squad | `/v1/fantasy_squad?id=` | NEW - Need payload |
| 13 | Series Squads | `/v1/series_squad?id=` | Need payload |
| 14 | Fantasy Scorecard | `/v1/fantasy_scorecard?id=` | Need payload |
| 15 | Player Info | `/v1/player_info?id=` | Need payload |
| 16 | Fantasy Ball-by-Ball | `/v1/fantasy_bbb?id=` | IN TESTING |
| 17 | Country List | `/v1/countries` | Low priority |

### API Rate Strategy:
- **Total Budget**: 2000 hits/day
- **Cheapest**: `cricScore` (lightweight polling)
- **Most Expensive (time)**: `match_points` (~2 sec response)
- **Most Data**: `match_scorecard` (~20KB per call)
- **Best Batch**: `series_info` (full schedule in 1 call)

---

## IMPORTANT NOTES
- API Key: `8397379b-fa88-4c9d-937f-c59bcade6576`
- Rate Limit: 2000 hits/day
- IPL 2026 Series ID: `87c62aac-bc3c-4738-ab93-19da0690488f`
- PSL 2026 Series ID: `8bfedb5a-500c-4f02-a5c3-17a3d731fe9c`
- `match_points` API is SLOW (~2s) — needs aggressive caching
- Fantasy points can be NEGATIVE
- Scorecard has full dismissal chain (batsman -> bowler -> catcher)
