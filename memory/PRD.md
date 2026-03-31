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
- AI Override Resolve (click contest -> AI answers -> admin edit -> submit)
- Template Type Badges, Manual Contest Creation inside Match, Quick Resolve All

### IPL Encyclopedia Search (DONE - March 31, 2026)
- **IPL Rhombus Button**: Deep blue diamond shape in bottom nav center, white "IPL" text, Orbitron font
- **Comprehensive Search Bar**: Searches across players, teams, matches, records from MongoDB. Debounced, with hint chips
- **IPL Records Section**: Batting (8 records), Bowling (4 records), Team/Special (6 records) - color-coded vibrant cards
- **Cap Winners Scroll**: Orange Cap + Purple Cap winners 2016-2025, horizontal scroll cards
- **Team Logos Grid**: All 10 IPL teams (5x2), clickable to TeamProfilePage
- **Star Players Grid**: 20 players with team-colored avatars, initials, role badges
- **TeamProfilePage**: Hero banner, stats strip, championship titles, team info, bilingual history essay
- **PlayerProfileView**: Hero header, stats grid, detailed career stats, teams history with logos

### Real IPL Data Seed (DONE - March 31, 2026)
- **20 players** with VERIFIED stats from iplt20.com, ESPNcricinfo, CricTracker
- **Key verified stats**: Kohli 8,661 runs (267 matches), Chahal 221 wickets (174 matches), Dhoni 278 matches (5,439 runs), Rohit 7,124 runs, Bumrah 183 wickets, Russell 174.18 SR
- **18 records** all verified: Highest Team Total = SRH 287/3 vs RCB (2024), Most Expensive = Rs 27 Cr Rishabh Pant (LSG 2025), Most Matches = 278 MS Dhoni
- **10 Cap Winners** (2016-2025) including 2025: Orange Cap = Sai Sudharsan 759 runs (GT), Purple Cap = Prasidh Krishna 25 wickets (GT)
- **RCB updated**: 1 title (2025 IPL win), history essay updated
- Force reseed endpoint: `/api/ipl/seed?force=true`

### Head-to-Head Comparison (DONE - March 31, 2026)
- Two player selector dropdowns with search filter
- VS badge between selectors
- Animated progress bars for each stat (Matches, Runs, Avg, SR, 50s, 100s, Sixes, Fours, Wickets, Catches)
- Verdict banner showing which player leads in more categories
- Bars color-coded by team colors, winner highlighted
- Smooth CSS transition animations (1s duration)

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
- `/app/backend/routers/ipl_router.py` - IPL search, records, players, caps, head-to-head APIs
- `/app/backend/services/ipl_data_seeder.py` - IPL data seeder (20 players, 18 records, 10 cap winners) - REAL VERIFIED DATA
- `/app/frontend/src/pages/SearchPage.jsx` - IPL search with records, teams, players, Head-to-Head
- `/app/frontend/src/components/HeadToHead.jsx` - Player comparison with animated bars
- `/app/frontend/src/pages/TeamProfilePage.jsx` - Comprehensive team profiles

## Credentials
- Super Admin: Phone `7004186276`, PIN `5524`
- Database: `crickpredict` (NOT `bharat11`)
