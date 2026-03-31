# Bharat 11 - Fantasy Cricket Prediction PWA

## Product Requirements Document

### Original Problem Statement
Build a Fantasy Cricket Prediction PWA called "Bharat 11" with:
- JWT-based authentication with phone + PIN
- Live match tracking with CricketData.org API
- Contest-based prediction system
- AI-powered commentary (GPT-5.2)
- Real-time updates via Socket.IO
- Admin dashboard with user management
- IPL Encyclopedia with real historical data
- WhatsApp sharing with premium card generation
- Heavy animations and cricket celebrations

### Core Architecture
- **Frontend**: React.js (PWA) with Tailwind CSS, Shadcn UI, Framer Motion
- **Backend**: FastAPI (Python) with Motor (async MongoDB)
- **Database**: MongoDB (`crickpredict`)
- **Real-time**: Socket.IO
- **AI**: GPT-5.2 via Emergent LLM Key for commentary
- **API**: CricketData.org for live match data (17 APIs integrated)

### What's Been Implemented

#### Authentication & Core
- [x] Phone + PIN login/register with JWT
- [x] Super Admin role system
- [x] Wallet system (virtual coins)

#### CricketData.org API Integration (COMPLETED - March 2026)
- [x] **series_info** — Full IPL 2026 schedule (70 matches) synced to DB
- [x] **match_scorecard** — Real batting/bowling data per innings
- [x] **match_info** — Toss, winner, scores, venue
- [x] **series_points** — IPL standings table
- [x] **series_squad** — All team squads (25+ players each)
- [x] **cricScore** — Live score ticker (45s cache)
- [x] **match_points** — Fantasy points per player (where available)
- [x] **match_bbb** — Ball-by-ball data
- [x] **player_info** — Career stats, batting/bowling style
- [x] **Auto-sync on startup** — 70 matches synced from series_info API
- [x] **MongoDB caching layer** — api_cache collection with TTL-based caching
- [x] **Team name normalization** — RCBW→RCB, KXIP→PBKS throughout

#### Matches & Contests
- [x] Match sync from CricketData.org (PRIMARY source, Cricbuzz removed)
- [x] Auto-contest generation (3-tier template system)
- [x] Contest joining & prediction submission
- [x] Auto-settlement engine (45s polling)
- [x] Leaderboard with real-time updates

#### Admin Panel
- [x] Dashboard with stats overview
- [x] Match management
- [x] Template & question management
- [x] Quick Resolve (AI bulk resolution)
- [x] User management tab

#### UX Features
- [x] IPL Encyclopedia (115+ real records, head-to-head comparison)
- [x] Cricket celebrations (Six, Four, Wicket animations)
- [x] Prediction streaks with diamond theme
- [x] Mood meter (Instagram-style polls)
- [x] Player profiles with stats
- [x] Service worker offline support
- [x] React.lazy/Suspense code splitting

#### WhatsApp Share Card (COMPLETED - March 2026)
- [x] Premium collectible card (Topps Chrome / NBA Top Shot aesthetic)
- [x] 9:16 portrait ratio, gold corners, oversized rank
- [x] Bento stats grid, accuracy bar, mood meter
- [x] html2canvas compatible, Share + Download buttons

#### AI Ball-by-Ball Commentary (COMPLETED - March 2026)
- [x] 4-tab system: Match Story, Phase Analysis, Timeline, MVPs
- [x] Phase analysis: Powerplay/Middle/Death breakdown
- [x] Momentum indicator, timeline with oversized overs
- [x] Star performers with animated ratings
- [x] Framer Motion animations throughout

### Credentials
- Super Admin: Phone `7004186276`, PIN `5524`
- Database: `crickpredict`

### Remaining/Backlog Tasks
1. **P1**: Redis caching layer for hot API responses
2. **P1**: Pagination improvements (backend + frontend)
3. **P2**: 200-question pool architecture
4. **P2**: Advanced template routing (full_match vs in_match)
5. **P2**: Socket.IO live score push via Redis pub/sub
