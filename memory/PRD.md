# Bharat 11 - Product Requirements Document

## Original Problem Statement
Build a Fantasy Cricket Prediction PWA called "Bharat 11" with:
1. 200 question pool with fixed points betting/prediction model
2. Advanced template routing (full_match vs in_match) with over/innings deadlines
3. Match Auto-Engine: 5 templates per match auto-attached 24h before start
4. Auto-settlement: AI agent auto-resolves questions from live scorecard
5. Real-time updates: Socket.IO for leaderboard + push notifications
6. Enhanced UX: AI commentary, heavy animations, WhatsApp sharing, Match Mood Meter
7. Admin features: Dashboard with auto/manual template building
8. IPL-ONLY matches enforced

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

### Phase 4: Auto-Settlement (DONE)
- Settlement engine polling every 45 seconds

### Phase 5-6: LOT 1-5 API Integration (DONE)
- Squads, Standings, Fantasy Points, Ball-by-Ball, IPL-only filtering

### Phase 7: AI Commentary + Animations (DONE - March 30, 2026)
- GPT-5.2 structured JSON commentary with match_pulse, key_moments, star_performers, turning_point, verdict
- LiveTab 3 sub-tabs (Match Story / Moments / Stars)
- Event animations (SIX golden glow, WICKET red shake, FOUR blue wave)
- Team card image backgrounds, glass morphism

### Phase 8: Match Mood Meter (DONE - March 30, 2026)
- Instagram-style live poll ("Who's winning today?")
- Backend: POST /api/matches/{id}/mood-vote, GET /api/matches/{id}/mood-meter
- Frontend: MoodMeter component with team logos, progress bar, VOTED badge
- Integrated into ShareCard for WhatsApp sharing

### Phase 9: HD Polish Stage 1-6 (DONE - March 30, 2026)
- Glass morphism clarity: darker backgrounds (rgba(22,22,30,0.65-0.75))
- Text contrast: secondary #C8C8C8, tertiary #808080
- Contest cards: participant progress bars, clearer entry fees
- Tab bar: glass morphism with active indicator dot
- Leaderboard: rounded avatar squares, bold names, gold ranking
- Player Profile Modal: better spacing, backdrop blur
- Fantasy Points tab: polished toggle + rows
- Dual Points Banner: animated gradient shift
- Match cards: team card image backgrounds with dark overlay
- Scorecard: clearer key metrics with color-tinted borders
- Score display: handles both r/w/o and runs/wickets/overs formats

## Prioritized Backlog

### P0 (Next Up)
- Socket.IO integration for real-time leaderboard and live score push
- Push notifications (match start, results)

### P1
- PWA polish (service worker, offline mode, install prompt)
- User Management tab in Admin Dashboard

### P2
- Advanced WhatsApp share card animations (confetti, rank reveal)
- Performance optimization / Lighthouse audit

## Architecture
```
/app/backend/
  routers/ (admin.py, cricket.py, matches.py, contests.py)
  services/ (cricket_data.py, match_engine.py, ai_commentary.py, settlement_engine.py, autopilot.py)
  models/schemas.py, core/ (security.py, dependencies.py)
/app/frontend/src/
  pages/ (HomePage.jsx, MatchDetailPage.jsx, LeaderboardPage.jsx, PlayerView.jsx)
  components/ (ShareCard.jsx, ScorecardView.jsx, MoodMeter.jsx)
  constants/ (design.js, teams.js)
  App.css, App.js
```

## Key API Endpoints
- /api/matches/{id}/mood-vote (POST, auth required)
- /api/matches/{id}/mood-meter (GET, public)
- /api/matches/{id}/ai-commentary (GET)
- /api/matches/{id}/bbb (GET)
- /api/cricket/standings (GET)
