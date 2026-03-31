# Bharat 11 - Fantasy Cricket Prediction PWA

## Original Problem Statement
Build a Fantasy Cricket Prediction PWA called "Bharat 11" with CricketData.org API, Canvas animations, prediction questions, contest management, auto-settlement, and real-time updates.

## Core Architecture
- **Frontend**: React.js (PWA) + Canvas Particle Engine + Web Audio API + Framer Motion
- **Backend**: FastAPI + MongoDB (Motor async)
- **Auth**: Phone + PIN JWT
- **API**: CricketData.org Premium (IPL only)

## What's Implemented

### Phase 1 - Core Platform (DONE)
- JWT auth, Admin panel (Dashboard/Content/Matches/Resolve/Users)
- CricketData.org API sync (IPL only, 100% accurate)

### Phase 2 - UI Animations (DONE)
- Canvas Particle Engine: Six, Four, Wicket, Winner
- Web Audio API: Stadium sound effects

### Phase 3 - Prediction Questions (DONE - 31 Mar 2026)
- 16 questions (user's EXACT Hindi text) in 1 full_match template
- Points: Easy=55 (2 Qs), Medium=70 (5 Qs), Hard=90 (9 Qs) = 1270 total

### Phase 4 - Admin Matches Section REBUILD (DONE - 31 Mar 2026)
- **2 Sub-Tabs**: Matches | Contests
- **3 Sections each**: LIVE | UPCOMING/OPEN | COMPLETED/LOCKED
- **Match Card 3 Actions**: Make Live | Add Contest (template select) | Make Unlive
- **Contest Card 5 Actions**: Make Live | Make Unlive | AI Resolve | AI Answers | Manual Resolve + Delete
- **Max 5 contests/match**: Enforced backend + frontend

### Phase 5 - Critical Bug Fixes (DONE - 31 Mar 2026)
- **Autopilot Manual Override**: Added `manual_override` flag to matches and contests. When admin manually changes status, autopilot and sync APIs respect this flag and skip auto-changes.
- **Join Contest Fix**: Backend now allows joining contests with status `open` OR `live` (was only `open`). Also fixed timezone-aware lock_time comparison.
- **Contest Fetch Fix**: Contests are fetched and displayed for matches regardless of status (live, upcoming, completed).
- **IST Date Fix**: Backend returns `start_time_ist` field with properly formatted IST time (e.g., "24 May 2026, 07:30 PM IST"). Frontend uses `timeZone: 'Asia/Kolkata'` for date formatting.
- **Match Sorting Fix**: Backend sorts by `start_time` descending (most recent first). Frontend re-sorts: upcoming ascending (nearest first), completed descending (most recent first).

## Key Endpoints
- POST /api/auth/check-phone, POST /api/auth/login
- GET /api/matches, PUT /api/matches/{id}/status
- GET /api/matches/{id}/contests
- GET /api/contests, POST /api/admin/contests
- PUT /api/admin/contests/{id}/status, DELETE /api/admin/contests/{id}
- POST /api/contests/{id}/join
- POST /api/matches/live/sync-ipl-schedule

## Pending Tasks
### P0: Frontend Prediction Cards (user-facing question answering)
### P1: Redis caching, MongoDB indexes, Socket.IO
### P2: WhatsApp Share, AI Commentary, Dual points banner
