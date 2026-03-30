# Bharat 11 - Product Requirements Document

## Original Problem Statement
Build a Fantasy Cricket Prediction PWA called "Bharat 11" with:
1. 200 question pool with fixed points betting/prediction model
2. Advanced template routing (full_match vs in_match) with over/innings deadlines
3. Match Auto-Engine: 5 templates per match auto-attached 24h before start
4. Auto-settlement: AI agent auto-resolves questions from live scorecard
5. Real-time updates: Socket.IO for leaderboard + push notifications
6. Enhanced UX: AI commentary, heavy animations, WhatsApp sharing, Match Mood Meter
7. Admin features: Dashboard with auto/manual template building, clickable KPIs
8. IPL-ONLY matches enforced
9. Global Prediction Accuracy Badge system

## Tech Stack
- Frontend: React.js (PWA), Tailwind CSS, Shadcn/UI
- Backend: FastAPI, MongoDB
- AI: GPT-5.2 via Emergent LLM for commentary
- External API: CricketData.org Premium

## What's Been Implemented

### Phase 1-2: Core Backend (DONE)
- 200 question seed with bilingual Hindi/English questions
- Template/Question schemas with over/innings deadline fields
- Match engine with rigid deadline enforcement

### Phase 3: Match Auto-Engine (DONE)
- 5-template auto-attach (1 full_match + 4 in_match) per match
- Default template fallback when no templates assigned
- Auto-contest creation 24h before match

### Phase 4: Auto-Settlement (DONE)
- Settlement engine polling every 45 seconds from live scorecard

### Phase 5-6: LOT 1-5 API Integration (DONE)
- Squads, Standings, Fantasy Points, Ball-by-Ball, IPL-only filtering

### Phase 7: AI Commentary + Animations (DONE - March 30, 2026)
- GPT-5.2 structured JSON commentary (match_pulse, key_moments, star_performers, turning_point, verdict)
- LiveTab 3 sub-tabs (Match Story / Moments / Stars)
- Event animations (SIX golden glow, WICKET red shake, FOUR blue wave)
- Team card image backgrounds, glass morphism

### Phase 8: Match Mood Meter (DONE - March 30, 2026)
- Instagram-style live poll ("Who's winning today?")
- Backend: POST /api/matches/{id}/mood-vote, GET /api/matches/{id}/mood-meter
- Frontend: MoodMeter component with team logos, progress bar, VOTED badge
- Integrated into ShareCard for WhatsApp sharing

### Phase 9: HD Polish Stage 1-6 (DONE - March 30, 2026)
- Glass morphism clarity: darker backgrounds for readability
- Text contrast boost, contest card progress bars
- Tab bar glass morphism, leaderboard polish

### Phase 10: Global Prediction Accuracy Badge (DONE - March 30, 2026)
- Ranks users by total correct answers across ALL contests (not contest wins)
- Rank 1 = Pink Diamond, Rank 2 = Gold, Rank 3 = Silver, Rank 4+ = Blue Crystal
- Badge shows: diamond SVG icon, rank, correct/attempted, accuracy bar, percentage
- Displayed on: HomePage (between greeting and banner), ShareCard (WhatsApp)
- Backend: GET /api/contests/global/my-badge, GET /api/contests/global/prediction-leaderboard

### Phase 11: Admin Dashboard Enhancement (DONE - March 30, 2026)
- All KPI stat cards clickable → navigate to relevant tabs
- Quick Actions with icons, labels, chevron arrows
- Workflow steps all clickable with step numbers and navigation
- Alert cards clickable for contest resolution and match prep

## Prioritized Backlog

### P0 (Next Up)
- Socket.IO integration for real-time leaderboard and live score push
- Push notifications (match start, results)

### P1
- PWA polish (service worker, offline mode, install prompt)
- User Management tab in Admin Dashboard

### P2
- WhatsApp share card confetti animations
- Performance optimization / Lighthouse audit

## Architecture
```
/app/backend/
  routers/ (admin.py, cricket.py, matches.py, contests.py)
  services/ (cricket_data.py, match_engine.py, ai_commentary.py, settlement_engine.py, autopilot.py)
  models/schemas.py, core/ (security.py, dependencies.py)
/app/frontend/src/
  pages/ (HomePage.jsx, MatchDetailPage.jsx, LeaderboardPage.jsx, PlayerView.jsx)
  pages/admin/ (AdminDashboard.jsx, AdminApp.jsx)
  components/ (ShareCard.jsx, ScorecardView.jsx, MoodMeter.jsx, PredictionBadge.jsx)
  constants/ (design.js, teams.js)
  App.css, App.js
```

## Key API Endpoints
- /api/contests/global/my-badge (GET, auth required)
- /api/contests/global/prediction-leaderboard (GET, public)
- /api/matches/{id}/mood-vote (POST, auth required)
- /api/matches/{id}/mood-meter (GET, public)
- /api/matches/{id}/ai-commentary (GET)
- /api/admin/templates (CRUD)
- /api/admin/questions (CRUD)
