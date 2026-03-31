# Bharat 11 - Fantasy Cricket Prediction PWA

## Original Problem Statement
Build a Fantasy Cricket Prediction PWA called "Bharat 11" with CricketData.org API, Canvas animations, prediction questions, contest management, auto-settlement, and real-time updates.

## Core Architecture
- **Frontend**: React.js (PWA) + Canvas Particle Engine + Web Audio API + Framer Motion
- **Backend**: FastAPI + MongoDB (Motor async) + Redis (aioredis)
- **Auth**: Phone + PIN JWT
- **API**: CricketData.org Premium (IPL only)
- **Performance**: Redis response caching + MongoDB compound indexes

## What's Implemented

### Phase 1 - Core Platform (DONE)
- JWT auth, Admin panel (Dashboard/Content/Matches/Resolve/Users)
- CricketData.org API sync (IPL only, 100% accurate)

### Phase 2 - UI Animations (DONE)
- Canvas Particle Engine: Six, Four, Wicket, Winner
- Web Audio API: Stadium sound effects

### Phase 3 - Prediction Questions (DONE)
- 16 questions (user's EXACT Hindi text) in 1 full_match template
- Points: Easy=55 (2), Medium=70 (5), Hard=90 (9) = 1270 total

### Phase 4 - Admin Matches Section (DONE)
- 2 Sub-Tabs: Matches | Contests
- 3 Sections each with actions
- Max 5 contests/match enforced

### Phase 5 - Bug Fixes (DONE - 31 Mar 2026)
- Autopilot Manual Override, Join Contest Fix, IST Date Fix, Match Sorting

### Phase 6 - UX Overhaul (DONE - 31 Mar 2026)
- IPL LIVE Ticker replaced with Upcoming/Completed tabs
- Contest Page redesigned with stats strip and filters
- Prediction submit fix (max_length 15→50)
- Homepage rearranged: Live Now at top, IPL Table below Fantasy Points

### Phase 7 - Performance Stack (DONE - 31 Mar 2026)
- **Redis Server**: Installed and connected via redis_cache.py
- **API Response Caching**: Live ticker (30s), Points table (5min), Matches list (60s), IPL data (10min)
- **Cache Invalidation**: Auto-invalidate on match/contest status changes
- **Performance Gain**: Live ticker 1.29s → 0.12s (10x faster!)
- **MongoDB Compound Indexes**: matches{status,start_time,manual_override}, contests{match_id,status,manual_override}, contest_entries{contest_id,total_points}
- **Smart Pagination**: has_more field, cursor-based with limit/page

### Phase 8 - Mobile-First Frontend (DONE - 31 Mar 2026)
- **Global CSS**: -webkit-tap-highlight-color: transparent, touch-action: manipulation, safe-area-inset support
- **Min Touch Targets**: All buttons 44px+ height (bottom nav 62px)
- **iOS Input Zoom Fix**: font-size: 16px on inputs
- **Safe Area**: paddingBottom: calc(70px + env(safe-area-inset-bottom))
- **PredictionPage**: Scrollable question dots, sticky bottom navigation
- **BottomNav**: py-3 with 48px minHeight per button

## Key Endpoints
- POST /api/auth/check-phone, POST /api/auth/login
- GET /api/matches (smart sorted, Redis cached), PUT /api/matches/{id}/status
- GET /api/matches/{id}/contests, /match-info
- GET /api/contests/{id}/questions (16 Hindi questions)
- POST /api/contests/{id}/join, /predict (max 50 predictions)
- GET /api/contests/user/my-contests
- GET /api/cricket/live-ticker (IST, Redis 30s)
- GET /api/cricket/ipl/points-table (Redis 5min)
- GET /api/wallet/balance, POST /api/wallet/claim-daily

## Pending Tasks
### P1: Socket.IO real-time push for live scores
### P2: WhatsApp Share, AI Commentary, Dual points banner
### P3: User Management tab improvements
