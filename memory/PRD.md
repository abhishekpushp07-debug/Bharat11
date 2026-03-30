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
10. Prediction Streak with multiplier bonus

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
- GPT-5.2 structured JSON commentary
- LiveTab 3 sub-tabs (Match Story / Moments / Stars)
- Event animations (SIX golden glow, WICKET red shake, FOUR blue wave)

### Phase 8: Match Mood Meter (DONE - March 30, 2026)
- Instagram-style live poll ("Who's winning today?")
- Backend + Frontend MoodMeter component

### Phase 9: HD Polish Stage 1-6 (DONE - March 30, 2026)
- Glass morphism, text contrast, contest card progress bars

### Phase 10: Global Prediction Accuracy Badge (DONE - March 30, 2026)
- Ranks users by total correct answers across ALL contests
- Pink Diamond #1, Gold #2, Silver #3, Blue Crystal #4+

### Phase 11: Admin Dashboard Enhancement (DONE - March 30, 2026)
- Clickable KPIs, Quick Actions, Workflow steps

### Phase 12: Prediction Streak (DONE - March 31, 2026)
- Global streak tracking across all contests
- Streak tiers: BUILD IT (0-2), WARMING UP (3-4), HOT STREAK (5-9, 2x), LEGENDARY (10+, 4x)
- Settlement engine auto-updates streaks on question resolution
- Bonus multiplier applied during auto-settlement (2x at 5+, 4x at 10+)
- "Streak King" banner on HomePage showing top streak holder
- Fire particles, glowing borders, pulsing animations
- Backend: GET /api/contests/global/top-streak, GET /api/contests/global/my-streak
- User model: prediction_streak, max_prediction_streak fields

## Prioritized Backlog

### P0 (Next Up)
- Stage 2-4 Rigorous Verification (Contest Auto-Live, Default Template Fallback, Answer Deadline)
- Socket.IO integration for real-time leaderboard and live score push

### P1
- Push notifications (match start, results)
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
  components/ (ShareCard.jsx, ScorecardView.jsx, MoodMeter.jsx, PredictionBadge.jsx, StreakBanner.jsx)
  constants/ (design.js, teams.js)
  App.css, App.js
```

## Key API Endpoints
- /api/contests/global/my-badge (GET, auth required)
- /api/contests/global/prediction-leaderboard (GET, public)
- /api/contests/global/top-streak (GET, public)
- /api/contests/global/my-streak (GET, auth required)
- /api/matches/{id}/mood-vote (POST, auth required)
- /api/matches/{id}/mood-meter (GET, public)
- /api/matches/{id}/ai-commentary (GET)
- /api/admin/templates (CRUD)
- /api/admin/questions (CRUD)
