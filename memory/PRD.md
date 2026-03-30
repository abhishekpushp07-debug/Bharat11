# Bharat 11 - Fantasy Cricket Prediction PWA

## Product Overview
IPL-focused fantasy cricket prediction platform where users predict match outcomes, earn coins, and compete on leaderboards. Real-time updates via Socket.IO with AI-powered commentary.

## Core Requirements
1. **Prediction Model**: 200-question pool with fixed points per question
2. **Template Routing**: `full_match` vs `in_match` templates with over/innings cutoffs
3. **Match Auto-Engine**: 5 templates auto-attach (1 full + 4 in-match per match)
4. **Auto-Settlement**: AI agent auto-resolves questions from live scorecard
5. **Real-Time Updates**: Socket.IO for leaderboard, live scores, push notifications
6. **Enhanced UX**: AI commentary, heavy animations, dual points banner, WhatsApp sharing
7. **Admin Dashboard**: Template management, user management, AI question generation
8. **IPL Only**: Only fetch and display IPL matches
9. **Legal Compliance**: Platform is 100% legal under Indian gaming law (no deposits/withdrawals)

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
│   ├── models/schemas.py (TemplateType, innings_range, over routing)
│   ├── routers/
│   │   ├── admin.py (Seed endpoint, 5-Template Engine, User management)
│   │   ├── auth.py (JWT auth with PIN)
│   │   ├── cricket.py (IPL data, team drill-down, match full-data)
│   │   ├── matches.py (Match CRUD, scorecard, BBB, AI commentary)
│   │   ├── contests.py (Contest management, streak)
│   │   └── notifications.py (Push notifications)
│   ├── services/
│   │   ├── api_cache.py (MongoDB caching layer for all API calls)
│   │   ├── cricket_data.py (CricketData.org API wrapper)
│   │   ├── question_seed.py (200 bilingual EN+HI questions)
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
│   │   │   ├── BottomNav.jsx (Legal tab with Scale icon)
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
│   │       ├── HomePage.jsx (Stories contests, Points table, ticker, team drill-down)
│   │       ├── WalletPage.jsx (Balance + transactions + 6-point Legal section)
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

### Session 1 Updates (Mar 30, 2026)
- **MongoDB API Cache Layer**: All CricketData.org API calls cached. Completed match data permanent. API quota conserved.
- **Team Drill-Down**: Click team in points table → see matches → click match → scorecard/squad/fantasy/AI commentary.
- **TEAM_COLORS Fix**: Arrays → objects {primary, secondary}. Team colors now apply correctly.
- **UI Polish**: Team-colored rows, vibrant ticker, bold fire icon SVG, sparkling red streak.

### Session 2 Updates (Mar 31, 2026)
- **Legal Page**: Bottom nav "Wallet" → "Legal" with Scale icon. Wallet content + 6-point Indian gaming law compliance section (bilingual EN+HI). Points: No deposits, No withdrawals, Entertainment/Skill-based, Information focus, Social gaming, IT Act compliant.
- **Hot Contests → Instagram Stories**: Circular cards with slow rotating ring animation. Team-colored gradients, horizontal scroll.
- **200-Question Pool Seeded**: `POST /api/admin/seed-question-pool` — 200 bilingual questions across 7 categories (batting=40, bowling=35, powerplay=25, death_overs=25, match=30, player_performance=25, special=20).
- **5-Template Match Engine**: `POST /api/admin/matches/{id}/auto-templates` — Generates exactly 5 templates per match: 1 full_match (15 Qs) + 4 in_match (10 Qs each = 40) = 55 total questions. Templates have innings_range, over_start/end, answer_deadline_over for phase routing.

## Key API Endpoints
- `POST /api/admin/seed-question-pool` — Seed 200 questions
- `POST /api/admin/matches/{id}/auto-templates` — 5-Template Engine
- `POST /api/admin/auto-templates-all` — Bulk template generation
- `GET /api/cricket/ipl/points-table` — IPL standings
- `GET /api/cricket/live-ticker` — Live IPL scores
- `GET /api/cricket/ipl/team/{short}/matches` — Team's IPL matches
- `GET /api/cricket/match/{id}/full-data` — Combined match data (17 APIs)
- `GET /api/cricket/cache-stats` — Cache statistics

## Remaining / Backlog
### P1 (Important)
- Performance optimization / Lighthouse audit
- Socket.IO connection stability improvements

### P2 (Nice to have)
- WhatsApp share card confetti effects
- Service worker offline page improvements
- Final cleanup (remove test data, production-ready state)
