# Bharat 11 - Product Requirements Document

## Original Problem Statement
Build a Fantasy Cricket Prediction PWA called "Bharat 11" with:
1. 200 question pool with fixed points betting/prediction model
2. Advanced template routing (full_match vs in_match) with over/innings deadlines
3. Match Auto-Engine: 5 templates per match auto-attached 24h before start
4. Auto-settlement: AI agent auto-resolves questions from live scorecard
5. Real-time updates: Socket.IO for leaderboard + push notifications
6. Enhanced UX: AI commentary, heavy animations, WhatsApp sharing
7. Admin features: Dashboard with auto/manual template building
8. IPL-ONLY matches enforced

## User Personas
- **Players**: IPL fans who predict match outcomes for points/coins
- **Super Admin**: Manages matches, templates, questions, contests

## Tech Stack
- Frontend: React.js (PWA), Tailwind CSS, Shadcn/UI
- Backend: FastAPI, MongoDB
- AI: GPT-5.2 via Emergent LLM for commentary
- External API: CricketData.org Premium

## What's Been Implemented

### Phase 1-2: Core Backend ✅
- 200 question seed with bilingual Hindi/English questions
- Template/Question schemas with over/innings deadline fields
- Match engine with rigid deadline enforcement

### Phase 3: Match Auto-Engine ✅
- 5-template auto-attach (1 full_match + 4 in_match) per match
- Auto-contest generation

### Phase 4: Auto-Settlement ✅
- Settlement engine polling every 45 seconds
- AI auto-resolution from live scorecard data

### Phase 5-6: LOT 1-5 API Integration ✅
- Squads, Standings, Fantasy Points, Ball-by-Ball
- IPL-only filtering enforced

### Phase 7: UI/UX Major Upgrade (March 30, 2026) ✅
- **AI Commentary**: GPT-5.2 generates structured JSON with match_pulse, key_moments (15+), star_performers, turning_point, verdict in dramatic Hinglish
- **LiveTab**: 3 sub-tabs (Match Story, Moments, Stars) with immersive cards
- **Event Animations**: SIX (golden glow), FOUR (blue wave), WICKET (red shake), MILESTONE (green), DRAMATIC (purple)
- **Match Card Hero**: Team card image backgrounds with glass morphism
- **Dual Points Banner**: Animated gradient Fantasy Points + Contest Coins
- **ShareCard**: WhatsApp sharing with team logos, rank, score, team image background
- **Score Format**: Handles both r/w/o and runs/wickets/overs API formats
- **Glass morphism + noise overlay** CSS classes
- Real IPL team logos integrated

## Prioritized Backlog

### P0 (Next Up)
- Socket.IO integration for real-time leaderboard and live score push
- Push notifications (match start, results)

### P1
- PWA polish (service worker, offline mode, install prompt)
- User Management tab in Admin Dashboard

### P2
- WhatsApp share card polish (confetti on win, animated rank reveal)
- Advanced leaderboard animations
- Performance optimization / Lighthouse audit

## Architecture
```
/app/backend/
  routers/ (admin.py, cricket.py, matches.py, contests.py)
  services/ (cricket_data.py, match_engine.py, ai_commentary.py, settlement_engine.py, autopilot.py)
  models/schemas.py
/app/frontend/src/
  pages/ (HomePage.jsx, MatchDetailPage.jsx, LeaderboardPage.jsx, PlayerView.jsx)
  components/ (ShareCard.jsx, ScorecardView.jsx)
  constants/ (design.js, teams.js)
  App.css (animations), App.js (routing)
```
