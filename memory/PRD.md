# Bharat 11 - Fantasy Cricket Prediction PWA

## Product Overview
Fantasy Cricket Prediction PWA with JWT auth, real-time Socket.IO, push notifications, Super Admin panel, IPL Encyclopedia (115+ records), and heavy visual animations.

## Architecture
- **Frontend**: React.js PWA (mobile-first, dark theme, code-split with React.lazy)
- **Backend**: FastAPI + MongoDB (`crickpredict` DB)
- **Real-Time**: python-socketio (ASGI)
- **PWA**: Service Worker with offline support, push notifications
- **API Cache**: Custom caching layer for CricketData API

## ALL FEATURES IMPLEMENTED

### Core Platform (DONE)
- JWT Auth (phone + PIN), Match sync, Contest CRUD, 567 bilingual questions
- Template system (Full Match / In-Match), Auto-settlement engine (45s polling)
- Socket.IO real-time, Push notifications (VAPID), API caching, Prediction streaks

### Super Admin Overhaul (DONE)
- Bulk Delete, Default Templates (5 slots), AI Override Resolve, Quick Resolve All
- Template Type Badges, Manual Contest Creation, Player View toggle

### IPL Encyclopedia (DONE)
- 115+ verified records across 8 categories (Batting, Bowling, Fielding, Team, Controversy, Fun, Champions, Auction)
- 20 players with real stats, 10 cap winners (2016-2025)
- Head-to-Head comparison with animated bars
- Rich storytelling team histories for all 10 IPL teams
- Tab-based record category UI with count badges

### Auto Template Generation (DONE - March 31, 2026)
- Integrated `generate_5_templates_for_match` into `auto_create_contests_24h` in match_engine.py
- 3-tier fallback: 1) Existing templates → 2) Default template fallback → 3) Auto-generate 5 templates from question pool
- Runs automatically for matches within 24h via autopilot

### Performance Optimization (DONE - March 31, 2026)
- React.lazy code splitting for 8 heavy pages (WalletPage, ProfilePage, MatchDetailPage, MyContestsPage, PredictionPage, LeaderboardPage, AdminApp, SearchPage)
- Suspense with PageLoader spinner fallback
- Non-blocking font loading (media='print' onload pattern)
- Preconnect hints for Google Fonts

### Heavy Animations - Celebrations (DONE - March 31, 2026)
- CelebrationOverlay component with 3 types: Six (fire red), Four (blue), Wicket (purple)
- Animated shock rings expanding outward
- Particle explosion with random angles, sizes, and team-colored particles
- Center badge with bounce-in animation and glow effects
- Auto-dismiss after 2.2 seconds with fade-out
- Triggered by tapping six/four/wicket badges in live commentary
- Also triggered via socket 'celebration' events during live matches

### WhatsApp Share Card Confetti (DONE - March 31, 2026)
- ConfettiEffect component with 40 falling particles
- 8 vibrant colors, random sizes/shapes/rotations/delays
- Automatically activates for top-3 rank finishes (isTop3 = rank <= 3)
- Integrated into ShareCard component

### Service Worker Offline Page (DONE - March 31, 2026)
- Comprehensive service worker with network-first strategy
- Offline HTML page with Bharat 11 branding (golden gradient, pulse animation)
- Retry Connection button
- Asset caching for repeat visits
- Push notification support via web-push

### User Management Tab (DONE - March 31, 2026)
- Admin Users tab added to AdminPage (7th tab)
- GET /api/admin/users — List all users with search by name/phone, pagination
- GET /api/admin/users/{user_id} — Detailed user profile with stats
- User list shows: name, phone, admin badge, total points, entries count
- User detail shows: predictions, correct count, accuracy %, wallet, rank, total points, entries
- Recent contest entries list with scores and ranks

## Key Files
- `/app/backend/routers/admin.py` - Admin APIs (2300+ lines) incl. user management
- `/app/backend/services/match_engine.py` - Auto contest creation with template generation fallback
- `/app/backend/services/template_engine.py` - 5-template generation engine
- `/app/backend/services/ipl_data_seeder.py` - 115 records, 20 players, 10 caps
- `/app/frontend/src/App.js` - React.lazy code splitting, Suspense
- `/app/frontend/src/components/CelebrationOverlay.jsx` - Six/Four/Wicket animations
- `/app/frontend/src/components/ConfettiEffect.jsx` - Falling confetti particles
- `/app/frontend/src/components/ShareCard.jsx` - WhatsApp share with confetti
- `/app/frontend/src/pages/admin/AdminUsersTab.jsx` - User management UI
- `/app/frontend/src/pages/MatchDetailPage.jsx` - Match detail with celebration triggers
- `/app/frontend/public/service-worker.js` - PWA service worker
- `/app/frontend/public/offline.html` - Offline page

## Credentials
- Super Admin: Phone `7004186276`, PIN `5524`
- Database: `crickpredict` (NOT `bharat11`)
