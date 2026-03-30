# Bharat 11 - Product Requirements Document

## Original Problem Statement
Build a Fantasy Cricket Prediction PWA called "Bharat 11" with 12-stage master plan:
1. IPL-Only Cleanup + Team Logo Integration
2. Answer Deadline Enforcement (over/innings cutoffs)
3. Max 11 Questions + Default Template Fallback
4. Contest Auto-Live 24h Before Match
5. Points & Leaderboard (Dream11 style)
6. Ball-by-Ball Commentary (LOT4 API)
7. Dual Points Banner + Player Profile Modal
8. Socket.IO Real-Time Updates
9. Heavy Animations (SIX/FOUR/WICKET)
10. WhatsApp Share Card
11. Push Notifications + PWA Polish
12. User Management + Final Polish

Plus extras: AI Commentary, Mood Meter, Prediction Badge, Prediction Streak.

## Tech Stack
- Frontend: React.js (PWA), Tailwind CSS, Shadcn/UI, html2canvas, socket.io-client
- Backend: FastAPI, MongoDB, python-socketio, pywebpush
- AI: GPT-5.2 via Emergent LLM for commentary
- External API: CricketData.org Premium

## COMPLETED STAGES (All 12 + 4 Extras)

### Stage 1-7: Core Features ✅
All verified in audit docs (100/100 scores).

### Stage 8: Socket.IO Real-Time ✅ (March 31, 2026)
- Backend: `services/socket_manager.py` with python-socketio AsyncServer
- ASGI wrapper: `combined_app = socketio.ASGIApp(sio, app, socketio_path='api/socket.io')`
- Events: `live_score`, `question_resolved`, `leaderboard_update`, `template_locked`, `contest_created`, `contest_finalized`
- Room management: `join_match`, `leave_match`, `join_contest`, `leave_contest`, `join_home`
- Frontend: `socketStore.js` Zustand store auto-connects on PlayerApp mount
- Live updates: HomePage (live scores, new contests), MatchDetailPage (scores, resolutions, locks), LeaderboardPage (rank updates)
- UI: Green "LIVE" / Red "OFFLINE" indicator on HomePage header
- Settlement engine emits `question_resolved` + `leaderboard_update` after auto-resolve
- Autopilot emits `contest_created` when auto-contest goes live
- Match engine emits `live_score` after scorecard fetch

### Stage 9: Heavy Animations ✅
SIX/FOUR/WICKET/Prize animations in App.css.

### Stage 10: WhatsApp Share Card ✅
html2canvas ShareCard with team logos.

### Stage 11: Push Notifications + PWA ✅ (March 31, 2026)
- Backend: `services/push_manager.py` with pywebpush
- VAPID keys generated and stored in .env
- Endpoints: `GET /api/notifications/vapid-public-key`, `POST /api/notifications/subscribe`, `POST /api/notifications/unsubscribe`
- Push triggers: `notify_match_starting`, `notify_results_ready`, `notify_contest_live` 
- Frontend: `hooks/usePushNotifications.js` hook with subscribe/unsubscribe
- Service worker: Cache-first/Network-first strategies, push handler, notification click handler
- UI: Bell icon toggle on HomePage header

### Stage 12: User Management ✅ (March 31, 2026)
- Backend: `GET /api/admin/users` (paginated, searchable, filterable)
- Backend: `GET /api/admin/users/{id}` (details + stats + prediction history)
- Backend: `POST /api/admin/users/{id}/ban` (toggle ban)
- Backend: `POST /api/admin/users/{id}/adjust-coins` (add/deduct with transaction log)
- Frontend: `AdminUsersTab.jsx` with search bar, banned filter, user rows
- Frontend: `UserDetailModal` with stats, ban toggle, coin adjustment
- Admin nav: 5 tabs (Dashboard, Content, Matches, Resolve, Users)

### Extra Features ✅
- Prediction Streak (2x at 5+, 4x at 10+, Streak King banner)
- AI Commentary (GPT Hinglish ball-by-ball)
- Match Mood Meter (live polling)
- Global Prediction Accuracy Badge (Pink Diamond/Gold/Silver)

## Architecture
```
/app/backend/
  server.py (combined_app = socketio.ASGIApp wrapping FastAPI)
  routers/ (admin.py, auth.py, cricket.py, matches.py, contests.py, notifications.py, user.py)
  services/ (cricket_data.py, match_engine.py, ai_commentary.py, settlement_engine.py, autopilot.py, socket_manager.py, push_manager.py)
  models/schemas.py, core/ (security.py, dependencies.py, database.py)
/app/frontend/src/
  App.js, App.css
  pages/ (HomePage.jsx, MatchDetailPage.jsx, LeaderboardPage.jsx, PlayerView.jsx, AdminApp.jsx)
  pages/admin/ (AdminDashboard.jsx, AdminContentPage.jsx, AdminMatchPage.jsx, AdminResolvePage.jsx, AdminUsersTab.jsx, etc.)
  components/ (ShareCard.jsx, ScorecardView.jsx, MoodMeter.jsx, PredictionBadge.jsx, StreakBanner.jsx)
  stores/ (authStore.js, socketStore.js, appStore.js)
  hooks/ (usePushNotifications.js)
  constants/ (design.js, teams.js)
```

## Key API Endpoints
### Public
- GET /api/socket.io/ (Socket.IO polling/websocket)
- GET /api/notifications/vapid-public-key
- GET /api/contests/global/prediction-leaderboard
- GET /api/contests/global/top-streak

### Auth Required
- GET /api/contests/global/my-badge
- GET /api/contests/global/my-streak
- POST /api/notifications/subscribe
- POST /api/notifications/unsubscribe

### Admin Required
- GET /api/admin/users (paginated, search, banned_only)
- GET /api/admin/users/{id} (detail + stats)
- POST /api/admin/users/{id}/ban
- POST /api/admin/users/{id}/adjust-coins

## Backlog
- Performance optimization (lazy loading, API pagination, MongoDB indexes)
- Lighthouse audit + PWA score optimization
- Share card confetti effects
- Service worker offline page improvements
