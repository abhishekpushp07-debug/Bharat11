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
- **IST Dates Fixed**: All times display in GMT+5:30 (Asia/Kolkata)
- **Date Corruption Fixed**: Schedule sync now ALWAYS updates start_time (was storing IST as UTC)
- **Status Fix**: PBKS vs GT correctly shows UPCOMING (was wrongly completed)
- **Match Unlive**: Backend allows live→upcoming transition
- **Auto Live/Unlive**: AutoPilot manages contest lifecycle (24hr auto-live, 6th over lock, interval lock)
- **Max 5 contests/match**: Enforced backend + frontend

## Key Endpoints
- POST /api/auth/check-phone, POST /api/auth/login
- GET /api/matches, PUT /api/matches/{id}/status
- GET /api/contests, POST /api/admin/contests
- PUT /api/admin/contests/{id}/status, DELETE /api/admin/contests/{id}
- POST /api/matches/live/sync-ipl-schedule

## Pending Tasks
### P0: Frontend Prediction Cards (user-facing question answering)
### P1: Redis caching, MongoDB indexes, Socket.IO
### P2: WhatsApp Share, AI Commentary, Dual points banner
