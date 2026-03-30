# LOT 2 — Extended API Documentation (Raw Payloads)
## Date: 2026-03-30

## Available API Endpoints (Full List from CricketData.org)

### List APIs
- `/v1/currentMatches` — Top Used (covered in LOT 1)
- `/v1/cricScore` — Top Used (covered in LOT 1)
- `/v1/series` — Series Search (with search param) (covered in LOT 1 + below)
- `/v1/series` — Series List (offset pagination)
- `/v1/matches` — Matches List (offset pagination)
- `/v1/players` — Players List (offset pagination)
- `/v1/players?search=` — Players Search

### Cricket Info APIs
- `/v1/series_info?id=` — Series Info (detailed with match list)
- `/v1/match_info?id=` — Match Info (detailed single match)
- `/v1/player_info?id=` — Player Info

### Fantasy APIs
- `/v1/fantasy_squad?id=` — Fantasy Squad (NEW)
- `/v1/series_squad?id=` — Series Squads
- `/v1/fantasy_scorecard?id=` — Fantasy Scorecard
- `/v1/fantasy_points?id=` — Fantasy Match Points
- `/v1/series_points?id=` — Series Point Table
- `/v1/fantasy_xi?id=` — Fantasy XI (DO NOT USE)
- `/v1/fantasy_bbb?id=` — Fantasy Ball-by-Ball (IN TESTING)

### Misc APIs
- `/v1/countries` — Country List

---

## API 1: Series List (with offset pagination)
**Endpoint**: `GET /v1/series?apikey={key}&offset=0`
**Purpose**: Browse all cricket series worldwide

**Sample Response**:
```json
{
  "data": [
    {
      "id": "c58c8862-0d1d-413a-88a5-bc84b11e3211",
      "name": "Australia Women tour of South Africa, 2027",
      "startDate": "2027-03-18",
      "endDate": "Apr 11",
      "odi": 3,
      "t20": 3,
      "test": 1,
      "squads": 0,
      "matches": 7
    }
  ],
  "info": {
    "hitsToday": 14,
    "hitsUsed": 1,
    "hitsLimit": 2000,
    "offsetRows": 0,
    "totalRows": 1004
  }
}
```

---

## API 2: Matches List (with offset pagination)
**Endpoint**: `GET /v1/matches?apikey={key}&offset=0`
**Purpose**: Browse ALL matches across all series (14403 total rows!)

**Sample Response**:
```json
{
  "data": [
    {
      "id": "814916d1-784a-4659-8a8c-1650562efc06",
      "name": "Lahore Qalandars vs Karachi Kings, 6th Match, Pakistan Super League 2026",
      "matchType": "t20",
      "status": "Karachi Kings won by 4 wkts",
      "venue": "Gaddafi Stadium, Lahore",
      "date": "2026-03-29",
      "dateTimeGMT": "2026-03-29T14:00:00",
      "teams": ["Lahore Qalandars", "Karachi Kings"],
      "teamInfo": [
        {"name": "Karachi Kings", "shortname": "KRK", "img": "https://g.cricapi.com/iapi/37-637992689033348642.webp?w=48"},
        {"name": "Lahore Qalandars", "shortname": "LHQ", "img": "https://g.cricapi.com/iapi/41-637991979136379824.webp?w=48"}
      ],
      "score": [
        {"r": 128, "w": 9, "o": 20, "inning": "lahore qalandars Inning 1"},
        {"r": 131, "w": 6, "o": 19.3, "inning": "Lahore Qalandars,Karachi Kings Inning 1"}
      ],
      "series_id": "8bfedb5a-500c-4f02-a5c3-17a3d731fe9c",
      "fantasyEnabled": true,
      "bbbEnabled": false,
      "hasSquad": true,
      "matchStarted": true,
      "matchEnded": true
    }
  ],
  "info": {
    "hitsToday": 16,
    "hitsUsed": 1,
    "hitsLimit": 2000,
    "totalRows": 14403
  }
}
```

---

## API 3: Players List (with offset + search)
**Endpoint**: `GET /v1/players?apikey={key}&offset=0&search={name}`
**Purpose**: Search players by name

**Sample Response**:
```json
{
  "data": [
    {
      "id": "562a3f59-f587-48ca-a0f1-3c1c40935ba9",
      "name": "Abhishek Srivastava",
      "country": "India"
    }
  ],
  "info": {
    "totalRows": 18014
  }
}
```

---

## API 4: Series Info (Detailed with Match List)
**Endpoint**: `GET /v1/series_info?apikey={key}&id={series_id}`
**Purpose**: Get full series details + all matches in that series

**Sample (PSL 2026 — id: 8bfedb5a-500c-4f02-a5c3-17a3d731fe9c)**:
```json
{
  "data": {
    "info": {
      "id": "8bfedb5a-500c-4f02-a5c3-17a3d731fe9c",
      "name": "Pakistan Super League 2026",
      "startdate": "2026-03-26",
      "enddate": "May 03",
      "odi": 0,
      "t20": 44,
      "test": 0,
      "squads": 8,
      "matches": 44
    },
    "matchList": [
      {
        "id": "0579cb05-5cd8-493e-a513-24c4d074394f",
        "name": "Lahore Qalandars vs Hyderabad Kingsmen, 1st Match, Pakistan Super League 2026",
        "matchType": "t20",
        "status": "Lahore Qalandars won by 69 runs",
        "venue": "Gaddafi Stadium, Lahore",
        "date": "2026-03-26",
        "dateTimeGMT": "2026-03-26T14:00:00",
        "teams": ["Lahore Qalandars", "Hyderabad Kingsmen"],
        "teamInfo": [...],
        "fantasyEnabled": true,
        "bbbEnabled": false,
        "hasSquad": true,
        "matchStarted": true,
        "matchEnded": true
      }
    ]
  }
}
```

**KEY INSIGHT**: `series_info` returns FULL match schedule for a series — perfect for fetching entire IPL schedule in 1 API call!

---

## API 5: Match Info (Detailed Single Match)
**Endpoint**: `GET /v1/match_info?apikey={key}&id={match_id}`
**Purpose**: Detailed info for a single match (scores, toss, winner, series_id)

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
      {"name": "Hobart Hurricanes Women", "shortname": "HB-W", "img": "..."},
      {"name": "Sydney Thunder Women", "shortname": "ST-W", "img": "..."}
    ],
    "score": [
      {"r": 92, "w": 10, "o": 17.4, "inning": "Sydney Thunder Women Inning 1"},
      {"r": 95, "w": 5, "o": 16, "inning": "Hobart Hurricanes Women Inning 1"}
    ],
    "tossWinner": "hobart hurricanes women",
    "tossChoice": "bowl",
    "matchWinner": "Hobart Hurricanes Women",
    "series_id": "f6f07506-8226-4882-8b03-fadb1e696826",
    "fantasyEnabled": true,
    "bbbEnabled": true,
    "hasSquad": true,
    "matchStarted": true,
    "matchEnded": true
  }
}
```

**KEY FIELDS**: `tossWinner`, `tossChoice`, `matchWinner`, `series_id`, `score[]`

---

## KNOWN SERIES IDs
- **IPL 2026**: `87c62aac-bc3c-4738-ab93-19da0690488f`
- **PSL 2026**: `8bfedb5a-500c-4f02-a5c3-17a3d731fe9c`

## API USAGE STRATEGY
- `cricScore` — Lightweight live feed (use for polling)
- `currentMatches` — Full recent matches with scores
- `series_info` — Get FULL IPL schedule in 1 call (74 matches)
- `match_info` — Detailed single match (toss, winner, series_id)
- `match_scorecard` — Full batting/bowling/catching (ALREADY IMPLEMENTED)
- `fantasy_scorecard` — Fantasy-specific scorecard
- `fantasy_points` — Fantasy match points
- `series_points` — Series point table
- `fantasy_bbb` — Ball-by-Ball (IN TESTING - could be useful for live over tracking)

## API RATE: 2000 hits/day
## API KEY: 8397379b-fa88-4c9d-937f-c59bcade6576
