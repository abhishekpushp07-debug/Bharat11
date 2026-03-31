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

## What's Been Implemented (as of 31 Mar 2026)

### Phase 1 - Core Platform (DONE)
- JWT auth (phone + PIN)
- Admin panel with Dashboard, Content, Matches, Resolve, Users tabs
- CricketData.org API sync (IPL only, 100% accurate mapping)
- Score field normalization (r/w/o vs runs/wickets/overs)

### Phase 2 - UI Animations (DONE)
- Canvas Particle Engine: Six, Four, Wicket, Winner celebrations
- Web Audio API: Stadium-level sound effects

### Phase 3 - Prediction System (DONE - 31 Mar 2026)
- **16 Questions Seeded** (user's exact Hindi text, verbatim):
  - 4 First Innings (in_match): Runs, Wickets, Sixes, Fours = 305 pts
  - 12 Full Match (full_match): Winner, Death Overs, Batting/Bowling stats = 965 pts
  - Total: 1270 points across 16 questions
- Points: Easy=55 (2), Medium=70 (5), Hard=90 (9)
- 2 Templates: First Innings Predictions + Full Match Predictions

### Phase 4 - Contest Management (DONE - 31 Mar 2026)
- Admin flow: Select Match → Add Contest → Select Template → Create
- Max 5, Min 1 contests per match (enforced backend + frontend)
- Single contest delete with confirmation
- Progress bar showing X/5 contests used
- Contest cards: name, template type badge, entry fee, participants, delete button
- Backend: POST /admin/contests (create), DELETE /admin/contests/{id} (delete)

## Pending / Upcoming Tasks

### P0 (Next)
- Frontend Prediction Cards: User-facing UI for answering seeded questions

### P1
- Redis caching layer for slow API endpoints
- MongoDB indexes for frequently queried collections
- Socket.IO integration for live score push
- Real-time leaderboard updates

### P2
- WhatsApp Share aesthetic card rendering (HTML to Canvas)
- AI Ball-by-ball commentary
- Dual points banner (Fantasy + Contest)
- Heavy UI animations for celebrations in prediction flow

## Key Endpoints
- POST /api/auth/check-phone, POST /api/auth/login
- GET /api/matches, GET /api/contests
- POST /api/admin/contests, DELETE /api/admin/contests/{id}
- GET /api/admin/templates, GET /api/admin/questions
- GET /api/admin/stats

## Database Collections
- users, matches, questions, templates, contests, contest_entries

## Credentials
- Super Admin: Phone 7004186276, PIN 5524
