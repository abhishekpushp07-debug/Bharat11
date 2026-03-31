# Bharat 11 - Fantasy Cricket Prediction PWA

## Product Overview
Fantasy Cricket Prediction PWA with JWT auth, real-time Socket.IO, push notifications, comprehensive Super Admin panel, and world-class IPL Encyclopedia search.

## Architecture
- **Frontend**: React.js PWA (mobile-first, dark theme)
- **Backend**: FastAPI + MongoDB (`crickpredict` DB)
- **Real-Time**: python-socketio (ASGI)
- **API Cache**: Custom caching layer for CricketData API

## What's Been Implemented

### Core Platform (DONE)
- JWT Auth (phone + PIN), Match sync, Contest CRUD, 567 bilingual questions
- Template system (Full Match / In-Match), Auto-settlement engine (45s polling)
- Socket.IO real-time, Push notifications (VAPID), API caching, Prediction streaks

### Super Admin Overhaul (DONE - March 30, 2026)
- Bulk Delete (multi-select for Questions, Templates, Contests)
- Default Templates (5 slots, auto-attach 24h before match)
- AI Override Resolve (click contest → AI answers → admin edit → submit)
- Template Type Badges, Manual Contest Creation inside Match, Quick Resolve All

### IPL Encyclopedia Search (DONE - March 31, 2026)
- **IPL Rhombus Button**: Deep blue diamond shape in bottom nav center, white "IPL" text, Orbitron font
- **Comprehensive Search Bar**: Searches across players, teams, matches, records from MongoDB. Debounced, with hint chips
- **IPL Records Section**: Batting (8 records), Bowling (4 records), Team/Special (6 records) - color-coded vibrant cards
- **Cap Winners Scroll**: Orange Cap + Purple Cap winners 2016-2024, horizontal scroll cards
- **Team Logos Grid**: All 10 IPL teams (5x2), clickable to TeamProfilePage
- **Star Players Grid**: 20 players with team-colored avatars, initials, role badges. Clickable to PlayerProfileView
- **TeamProfilePage**: Hero banner, stats strip, championship titles, team info, bilingual history essay, key players scroll, fun facts, matches
- **PlayerProfileView**: Hero header, stats grid, detailed career stats, teams history with logos, achievements, bilingual bio
- **Backend Data**: 20 IPL players, 18 records, 9 cap winner years seeded in MongoDB

## Remaining Tasks
### P1
- Performance optimization / Lighthouse audit
- Auto template generation (full_match/in_match intervals)

### P2
- Heavy animations (sixes/wickets/fours celebrations)
- WhatsApp share card confetti effects
- Service Worker offline page
- User Management Tab

## Key Files
- `/app/backend/routers/admin.py` - Admin APIs (2300+ lines)
- `/app/backend/routers/ipl_router.py` - IPL search, records, players, caps APIs
- `/app/backend/services/ipl_data_seeder.py` - IPL data seeder (20 players, 18 records)
- `/app/frontend/src/pages/SearchPage.jsx` - IPL search with records, teams, players
- `/app/frontend/src/pages/TeamProfilePage.jsx` - Comprehensive team profiles
- `/app/frontend/src/components/BottomNav.jsx` - IPL rhombus button

## Credentials
- Super Admin: Phone `7004186276`, PIN `5524`
- Database: `crickpredict` (NOT `bharat11`)
