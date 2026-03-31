# Bharat 11 - Fantasy Cricket Prediction PWA

## Product Requirements Document

### Original Problem Statement
Build a Fantasy Cricket Prediction PWA called "Bharat 11" with comprehensive CricketData.org API integration, AI commentary, real-time updates, admin dashboard, and premium UX.

### Core Architecture
- **Frontend**: React.js (PWA) + Tailwind CSS + Shadcn UI + Framer Motion
- **Backend**: FastAPI + Motor (async MongoDB)
- **Database**: MongoDB (`crickpredict`)
- **Real-time**: Socket.IO
- **AI**: GPT-5.2 via Emergent LLM Key
- **API**: CricketData.org (17 APIs integrated)

### What's Been Implemented

#### CricketData.org API Integration (COMPLETED - March 2026)
- [x] **series_info** — 70 IPL matches synced, auto-sync on startup
- [x] **match_scorecard** — Real batting/bowling data (11 batsmen per team)
- [x] **match_info** — Toss, winner, scores, venue
- [x] **series_points** — IPL standings table (RCBW->RCB normalized)
- [x] **series_squad** — All team squads (25+ players each)
- [x] **cricScore** — Live score ticker (IPL-only filtering)
- [x] **match_points** — Fantasy points per player
- [x] **match_bbb** — Ball-by-ball data
- [x] **player_info** — Career stats
- [x] **Auto-sync startup** — 70 matches + score fetching for completed
- [x] **MongoDB indexes** — api_cache (compound unique), matches.cricketdata_id (sparse)

#### Data Accuracy Fix (COMPLETED - March 31, 2026)
- [x] **_align_team_info()** — Fixes CricketData API bug where teams[] and teamInfo[] arrays are in random different orders. Matches by canonical short name comparison.
- [x] **_is_strictly_ipl()** — Strict whitelist of 10 IPL team short names. BOTH teams must match. Filters out Pakistan Super League, Nigeria T20, etc.
- [x] **Score protection** — Never overwrites non-zero scores with zeros from series_info API
- [x] **Duplicate prevention** — sync_live_matches checks both external_match_id AND cricketdata_id + team name matching before creating
- [x] **DB correction** — All existing swapped matches corrected (1 match: MI vs KKR was swapped)
- [x] **Score normalization** — Both r/runs and w/wickets fields are consistently populated
- [x] Result: 100% IPL matches, 0 non-IPL, 0 duplicates, 0 team swaps

#### AI Commentary (COMPLETED - March 2026)
- [x] 4-tab system: Match Story, Phase Analysis, Timeline (16 moments), MVPs
- [x] Phase Analysis: Powerplay (1-6), Middle (7-15), Death (16-20)
- [x] Bilingual Hinglish commentary
- [x] Framer Motion animations

#### WhatsApp Share Card (COMPLETED - March 2026)
- [x] Premium collectible card (Topps Chrome aesthetic)
- [x] 9:16 portrait, gold corners, oversized rank, bento stats

#### Auth, Matches, Contests, Admin, UX — All complete

### Credentials
- Super Admin: Phone `7004186276`, PIN `5524`
- Database: `crickpredict`

### Remaining/Backlog Tasks
1. **P1**: Redis caching layer for hot API responses
2. **P1**: Pagination improvements (backend + frontend)
3. **P2**: 200-question pool architecture
4. **P2**: Advanced template routing (full_match vs in_match)
5. **P2**: Socket.IO live score push via Redis pub/sub
