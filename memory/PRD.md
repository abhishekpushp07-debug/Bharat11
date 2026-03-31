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
- [x] **series_points** — IPL standings table (RCBW→RCB normalized)
- [x] **series_squad** — All team squads (25+ players each)
- [x] **cricScore** — Live score ticker (IPL-only filtering)
- [x] **match_points** — Fantasy points per player
- [x] **match_bbb** — Ball-by-ball data
- [x] **player_info** — Career stats
- [x] **Auto-sync startup** — 70 matches + score fetching for completed
- [x] **Team name fix** — teams[] vs teamInfo[] order mismatch fixed (28 matches corrected)
- [x] **Score fetching** — Auto-fetch from match_scorecard for completed matches with zeros
- [x] **Orphan cleanup** — Cricbuzz matches deleted, duplicates resolved
- [x] **MongoDB indexes** — api_cache (compound unique), matches.cricketdata_id (sparse)

#### AI Commentary (COMPLETED - March 2026)
- [x] 4-tab system: Match Story, Phase Analysis, Timeline (16 moments), MVPs
- [x] Phase Analysis: Powerplay (1-6), Middle (7-15), Death (16-20)
- [x] Momentum indicator, timeline with oversized overs
- [x] Star performers: Virat Kohli 9.6, Padikkal 9.4, Kishan 9.2
- [x] Bilingual Hinglish commentary ("Kohli-Padikkal chase: Chinnaswamy on fire!")
- [x] Framer Motion animations

#### WhatsApp Share Card (COMPLETED - March 2026)
- [x] Premium collectible card (Topps Chrome aesthetic)
- [x] 9:16 portrait, gold corners, oversized rank, bento stats

#### Auth, Matches, Contests, Admin, UX — All complete (see CHANGELOG.md)

### Credentials
- Super Admin: Phone `7004186276`, PIN `5524`
- Database: `crickpredict`

### Remaining/Backlog Tasks
1. **P1**: Redis caching layer for hot API responses
2. **P1**: Pagination improvements (backend + frontend)
3. **P2**: 200-question pool architecture
4. **P2**: Advanced template routing (full_match vs in_match)
5. **P2**: Socket.IO live score push via Redis pub/sub
