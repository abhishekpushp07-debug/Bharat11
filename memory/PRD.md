# Bharat 11 - Product Requirements Document

## Original Problem Statement
Fantasy Cricket Prediction PWA (IPL-only). "World's Best" standard. Complete Admin + Player separation. Auto-pipeline: Live match sync, auto-contests, real-time auto-settlement. Virtual Economy with 1 Lakh signup bonus. Dual-source live data: Cricbuzz (Primary) + CricketData.org Premium API.

## Architecture
- Frontend: React PWA (Tailwind CSS, Zustand, Shadcn/UI)
- Backend: FastAPI + MongoDB
- Data: BeautifulSoup4 Cricbuzz Scraper + CricketData.org Premium API (17+ APIs from LOT1-5)
- Auth: Phone + PIN JWT auth with role-based routing

## What's Implemented

### Core Infrastructure (Stages 1-14)
- JWT Auth (Phone+PIN), role-based routing (Admin/Player)
- Admin Dashboard (Dashboard, Content, Matches, Resolve tabs)
- Player View (zero admin traces, bottom nav)
- Template system (full_match/in_match, default, editable)
- Contest system with dynamic prize pools
- Economy system (1L signup, 1000 entry, 50/30/20 prize split)
- Dual-source data fetching (Cricbuzz BS4 + CricketData.org API)
- Auto-contest creation on match sync

### Auto-Settlement Engine (Layers 3 & 4)
- CricketData.org Premium Scorecard API integration
- Scorecard parser: 40+ metrics per match
- Question auto_resolution: metric + trigger + resolution_type
- Auto-resolve questions + auto-finalize contests + auto-distribute prizes
- Admin Resolve page with Auto-Settle + Manual tabs
- Auto-Pilot Mode: 45s polling loop

### 200-Question Pool + 5-Template Auto-Engine (2026-03-30)
- 200 bilingual T20 prediction questions across 7 categories
- Template Schema: innings_range, over_start, over_end, answer_deadline_over, phase_label
- 5-Template Auto-Engine per match (1 full_match + 4 in_match)
- Admin UI: Seed 200 button, Auto 5 Templates per match
- Testing: 100% pass (iteration_20)

### CricketData.org Full API Integration — LOT1 to LOT5 (2026-03-30)
All 17 APIs from LOT1-LOT5 documents integrated:

**Backend APIs Created:**
- `GET /api/cricket/ipl/points-table` — 10 IPL team standings (P/W/L/NR, team logos). LOT3 API 3.
- `GET /api/cricket/live-ticker` — Lightweight live score feed (12 IPL matches). LOT1 API 2.
- `GET /api/cricket/ipl/schedule` — Full 74-match IPL schedule. LOT2 API 4.
- `GET /api/cricket/ipl/squads` — All 10 IPL team squads with player details. LOT5 API 3.
- `GET /api/cricket/player/{player_id}` — Player profile + career stats. LOT5 API 1.
- `GET /api/matches/{id}/squad` — Match squad (2 teams, player photos, roles). LOT5 API 2.
- `GET /api/matches/{id}/fantasy-points` — Player fantasy points per innings. LOT3 API 2.
- `GET /api/matches/{id}/match-info` — Toss winner/choice, match winner, scores. LOT2 API 5.
- Caching: 60s live, 30min points table, 1hr squads/schedule.

**Frontend Features Built:**
1. **Live IPL Ticker** — Horizontal scroll banner on HomePage showing 12 IPL matches with team logos, scores, status
2. **IPL 2026 Standings** — Points table on HomePage with team logos, P/W/L/NR columns, "View All" toggle
3. **Match Cards** — Team-color gradients (MI blue, CSK yellow, RCB red etc.), countdown timer, live/completed states
4. **4-Tab Match Detail** — Contests | Scorecard | Squad | Fantasy Pts
5. **Toss + Result Info** — Hero card shows toss winner/choice + match winner
6. **Squad Tab** — Team selector buttons, players grouped by role (WK/Batters/AR/Bowlers), player photos, country, batting/bowling style
7. **Fantasy Points Tab** — Top Performers ranked list + innings breakdown (batting/bowling/catching)
8. **Scorecard Tab** — Full batting/bowling/catching stats per innings (using ScorecardView component)

Testing: 100% pass (iteration_21, 11/11 backend + 12/12 frontend)

## Key API Endpoints

### Auth
- POST /api/auth/check-phone, /api/auth/register, /api/auth/login

### Cricket Data (Public)
- GET /api/cricket/ipl/points-table
- GET /api/cricket/live-ticker
- GET /api/cricket/ipl/schedule
- GET /api/cricket/ipl/squads
- GET /api/cricket/player/{player_id}

### Match Detail (Public)
- GET /api/matches/{id}/squad
- GET /api/matches/{id}/fantasy-points
- GET /api/matches/{id}/match-info
- GET /api/matches/{id}/scorecard

### Admin
- POST /api/admin/seed-200-questions
- POST /api/admin/matches/{id}/auto-templates
- POST /api/admin/auto-templates-all
- POST /api/admin/autopilot/start|stop
- POST /api/admin/settlement/{id}/run

## Backlog

### P0 - Phase 4: Points & Leaderboard Upgrade
- Points = correct_answer x question_points (use question's point value)
- Real-time leaderboard calculation

### P1 - Phase 5: Socket.IO Integration
- Live score push, resolution events, leaderboard rank changes

### P1 - Phase 6: UX Enhancements
- Dual points banner (Fantasy + Contest), AI ball-by-ball commentary

### P2 - Phase 7: WhatsApp Sharing
- HTML-to-Canvas aesthetic card generation with rank and score

### P2 - Phase 8: UI Animations
- Heavy visual feedback (sixes, wickets, prize winners)

### P2 - PWA Polish & Notifications
- PWA manifest, offline caching, push notifications
- User Management tab (ban/unban, coin adjust)
