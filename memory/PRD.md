# Bharat 11 - Fantasy Cricket Prediction PWA

## Product Overview
IPL-focused fantasy cricket prediction platform where users predict match outcomes, earn coins, and compete on leaderboards. Real-time updates via Socket.IO with AI-powered commentary.

## Core Requirements
1. **Prediction Model**: 200-question pool with fixed points per question
2. **Template Routing**: `full_match` vs `in_match` templates with over/innings cutoffs
3. **Match Auto-Engine**: 5 templates auto-attach 24h before match start
4. **Auto-Settlement**: AI agent auto-resolves questions from live scorecard
5. **Real-Time Updates**: Socket.IO for leaderboard, live scores, push notifications
6. **Enhanced UX**: AI commentary, heavy animations, dual points banner, WhatsApp sharing
7. **Admin Dashboard**: Template management, user management, AI question generation
8. **IPL Only**: Only fetch and display IPL matches

## Tech Stack
- Frontend: React.js, Tailwind CSS, Shadcn/UI, Socket.IO client
- Backend: FastAPI, Motor (async MongoDB), python-socketio
- Database: MongoDB
- External: CricketData.org API (Premium), Emergent LLM Key (AI Commentary)
- Push: VAPID Web Push Notifications

## Architecture
```
/app/
├── backend/
│   ├── config/settings.py
│   ├── core/database.py
│   ├── models/schemas.py
│   ├── routers/
│   │   ├── admin.py (User management, template CRUD)
│   │   ├── auth.py (JWT auth with PIN)
│   │   ├── cricket.py (IPL data, team drill-down, match full-data)
│   │   ├── matches.py (Match CRUD, scorecard, BBB, AI commentary)
│   │   ├── contests.py (Contest management, streak)
│   │   └── notifications.py (Push notifications)
│   ├── services/
│   │   ├── api_cache.py (MongoDB caching layer for all API calls)
│   │   ├── cricket_data.py (CricketData.org API wrapper)
│   │   ├── settlement_engine.py (Auto-resolve + streak multiplier)
│   │   ├── ai_commentary.py (LLM-powered match commentary)
│   │   ├── socket_manager.py (Socket.IO event emitter)
│   │   ├── push_manager.py (Web Push notifications)
│   │   ├── match_engine.py (Match sync engine)
│   │   └── autopilot.py (Background task scheduler)
│   └── server.py (ASGI app with Socket.IO wrapper)
├── frontend/
│   ├── public/service-worker.js
│   ├── src/
│   │   ├── components/
│   │   │   ├── StreakBanner.jsx (Fire icon SVG, sparkling count)
│   │   │   └── PredictionBadge.jsx
│   │   ├── constants/
│   │   │   ├── teams.js (TEAM_COLORS {primary, secondary})
│   │   │   └── design.js
│   │   ├── hooks/usePushNotifications.js
│   │   ├── stores/
│   │   │   ├── authStore.js
│   │   │   └── socketStore.js
│   │   └── pages/
│   │       ├── HomePage.jsx (Points table, ticker, team drill-down, match data view)
│   │       ├── MatchDetailPage.jsx
│   │       ├── MyContestsPage.jsx
│   │       └── admin/AdminUsersTab.jsx
```

## What's Implemented
### Stages 1-14 (COMPLETE)
- JWT Auth with phone/PIN
- Match/Contest/Template/Question CRUD
- Auto-settlement engine with scorecard parsing
- Auto-pilot background tasks
- Socket.IO real-time (live scores, contest events)
- Web Push Notifications (VAPID)
- Admin User Management
- AI Ball-by-ball Commentary
- Prediction Streak with multipliers
- Prediction Badge (accuracy ranking)
- Mood Meter (prediction sentiment)

### Session Updates (Mar 30, 2026)
- **MongoDB API Cache Layer** (api_cache.py): All CricketData.org API calls cached in MongoDB. Completed match data cached permanently. Live match data with short TTL. Prevents duplicate API hits — saves API quota.
- **Team Drill-Down**: Click any team in IPL points table → see all 14 matches. Click any match → see full data (scorecard, squad, fantasy points, match info, metrics).
- **Match Full Data View**: Combined endpoint fetches match_info + scorecard + fantasy_points + squad + BBB in parallel. Tabbed UI with Info, Scorecard, Squad, Fantasy, AI Commentary.
- **TEAM_COLORS Fix**: Changed from arrays to objects {primary, secondary}. Fixed bug where team colors weren't applying to points table rows.
- **UI Polish**: Team-colored rows in points table, vibrant live ticker with team-color accents, bold fire icon (orange/yellow/red gradient SVG), sparkling red streak count.
- **Cache Stats Endpoint**: /api/cricket/cache-stats shows total cached items, by type, API hits today/remaining.

## Key API Endpoints
- `GET /api/cricket/ipl/points-table` — IPL standings
- `GET /api/cricket/live-ticker` — Live IPL scores
- `GET /api/cricket/ipl/team/{short}/matches` — Team's IPL matches
- `GET /api/cricket/match/{id}/full-data` — Combined match data (17 APIs)
- `GET /api/cricket/ipl/squads` — All team squads
- `GET /api/cricket/cache-stats` — Cache statistics
- `GET /api/matches/{id}/scorecard` — Match scorecard
- `GET /api/matches/{id}/ai-commentary` — AI-generated commentary

## Remaining / Backlog
### P0 (Critical)
- 200-Question Pool seed (question_seed.py) — bilingual Hindi+English
- Template routing schema upgrades (template_type, innings_range, over_start/end)
- 5-Template Match Engine (1 full_match + 4 in_match per match)

### P1 (Important)
- Performance optimization / Lighthouse audit
- Socket.IO connection stability improvements

### P2 (Nice to have)
- WhatsApp share card confetti effects
- Service worker offline page improvements
- Final cleanup (remove test data, production-ready state)
