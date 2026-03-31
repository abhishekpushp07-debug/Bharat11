# Bharat 11 - Fantasy Cricket Prediction PWA

## Original Problem Statement
Build a Fantasy Cricket Prediction PWA called "Bharat 11" with:
1. CricketData.org API integration (IPL men's matches only)
2. Heavy Canvas-based UI animations (Six, Four, Wicket, Prize) + Sound Effects
3. Fixed prediction question pool seeded with difficulty points (Hard=90, Medium=70, Easy=55)
4. Advanced template routing (full_match vs in_match)
5. Match Auto-Engine with 5 templates per match
6. Auto-settlement via AI agent from scorecard
7. Real-time updates (Socket.IO)
8. WhatsApp sharing, AI commentary, dual points banner

## Core Architecture
- **Frontend**: React.js (PWA) with Canvas Particle Engine, Web Audio API, Framer Motion
- **Backend**: FastAPI with MongoDB (Motor async driver)
- **Auth**: Phone + PIN based JWT auth
- **API**: CricketData.org Premium API for live match data

## What's Been Implemented

### Phase 1 - Core Platform (DONE)
- JWT auth (phone + PIN)
- Admin panel with Dashboard, Content, Matches, Resolve, Users tabs
- CricketData.org API sync (IPL only, 100% accurate mapping)
- Score field normalization (r/w/o vs runs/wickets/overs)

### Phase 2 - UI Animations (DONE)
- Canvas Particle Engine: Six, Four, Wicket, Winner celebrations
- Web Audio API: Stadium-level sound effects

### Phase 3 - Prediction System (DONE - 31 Mar 2026)
- **16 Questions Seeded** (user's exact Hindi text, verbatim) in **1 full_match template**
  - Q1-Q4: पहली पारी questions (Runs, Wickets, Sixes, Fours)
  - Q5-Q16: मैच questions (Winner, Death Overs, Batting/Bowling stats, Century, Extras)
  - Total: 1270 points (Easy=55x2, Medium=70x5, Hard=90x9)
  - 1 Template: "Full Match Predictions" (full_match, 16 Qs)

### Phase 4 - Contest Management (DONE - 31 Mar 2026)
- **Flow**: Select Match → Add Contest (select template) → Make Live → Lock
- **Manual Live/Unlive**: Contest cards have status toggle: Open ↔ Live ↔ Locked
- **Auto Live/Unlive** (AutoPilot):
  - 24hr before match → auto "live"
  - Full_match: After 1st innings 6th over → auto "locked"
  - In_match: Before innings interval → auto "locked"
- **Template + Questions View**: Click template badge → expands 16 questions with options
- **Answer Provision**: Can select options and submit answers from admin contest view
- Max 5, Min 1 contests per match enforced (backend + frontend)
- Single contest delete with confirmation
- API dedup fix: Same teams on different dates create separate matches

### Key Endpoints
- POST /api/auth/check-phone, POST /api/auth/login
- GET /api/matches, GET /api/contests
- POST /api/admin/contests, DELETE /api/admin/contests/{id}
- PUT /api/admin/contests/{id}/status (open/live/locked/cancelled)
- GET /api/admin/templates, GET /api/admin/questions

## Pending / Upcoming Tasks

### P0 (Next)
- Frontend Prediction Cards: User-facing match page with prediction questions for players

### P1
- Redis caching layer for slow API endpoints
- MongoDB indexes for frequently queried collections
- Socket.IO integration for live score push
- Real-time leaderboard updates

### P2
- WhatsApp Share aesthetic card rendering (HTML to Canvas)
- AI Ball-by-ball commentary
- Dual points banner (Fantasy + Contest)
- Heavy UI animations in prediction flow

## Credentials
- Super Admin: Phone 7004186276, PIN 5524
