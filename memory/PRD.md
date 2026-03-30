# Bharat 11 - Fantasy Cricket Prediction PWA

## Product Overview
Fantasy Cricket Prediction PWA with JWT auth, real-time Socket.IO, push notifications, and comprehensive Super Admin panel.

## Core Requirements
1. **Prediction Model**: 500+ bilingual question pool (Hindi+English), up to 11 questions per template
2. **Template Routing**: `full_match` vs `in_match` templates with innings/over cutoffs
3. **Match Auto-Engine**: Auto-attach 5 default templates 24h before match start
4. **Auto-Settlement**: AI agent reads scorecard + BBB to auto-resolve questions, with admin override
5. **Real-Time**: Socket.IO for live scores, leaderboards, push notifications
6. **Enhanced UX**: Dual points banner, team search, Hot Contests (Instagram stories style)
7. **Super Admin**: Full CRUD with multi-select delete, Default Templates, AI Override Resolve

## Architecture
- **Frontend**: React.js PWA (mobile-first)
- **Backend**: FastAPI + MongoDB (`crickpredict` DB)
- **Real-Time**: python-socketio (ASGI)
- **API Cache**: Custom caching layer for CricketData API (2000 hits/day limit)

## What's Been Implemented

### Phase 1-3: Core Platform (DONE)
- JWT Auth with phone + PIN
- Match sync from CricketData API
- Contest CRUD + entry system
- Question pool (567 bilingual questions seeded)
- Template system with Full Match / In-Match types
- Auto-settlement engine with 45s polling autopilot
- Socket.IO real-time events
- Push notifications (VAPID)
- API caching layer
- Prediction streaks + accuracy badges

### Phase 4: Super Admin Overhaul (DONE - March 30, 2026)
- **Bulk Delete**: Multi-select checkboxes + bulk delete for Questions, Templates, Contests
- **Default Templates**: Section to define 5 default templates (auto-attach 24h before match)
- **AI Override Resolve**: Click contest → see AI-predicted answers from scorecard → edit → submit
- **Template Type Badges**: Full Match / In-Match badges on all contest cards
- **Manual Contest Creation**: Create contests inside match view with default template options (prefixed "Default")
- **Enriched Contest List**: Template type, match label, question count in admin contest list
- **24h Auto-Engine**: Uses default templates as fallback, then copies from last match

### Phase 5: Player Search & UI (DONE - March 30, 2026)
- **Protruding Search Button**: Center of bottom nav, red gradient with glow effect
- **Search Page**: IPL team logos grid (10 teams, 5 columns), match search, quick stats
- **Dual Points Banner**: Fantasy Points + Contest Coins on homepage (gradient cards)

## Remaining Tasks

### P1 (Next Priority)
- Performance optimization / Lighthouse audit
- Template auto-generation following full_match/in_match intervals

### P2 (Future)
- Heavy animations (sixes/wickets/fours celebrations)
- WhatsApp share card confetti effects
- Service Worker offline page improvements
- User Management Tab (Admin Dashboard)

## Key Files
- `/app/backend/routers/admin.py` - Admin API endpoints (2100+ lines)
- `/app/backend/services/settlement_engine.py` - Auto-resolution engine
- `/app/backend/services/match_engine.py` - 24h auto-engine with default templates
- `/app/frontend/src/pages/AdminApp.jsx` - Admin shell
- `/app/frontend/src/pages/admin/AdminResolvePage.jsx` - AI Override resolve
- `/app/frontend/src/pages/SearchPage.jsx` - Player search page
- `/app/frontend/src/components/BottomNav.jsx` - Protruding search nav

## Credentials
- Super Admin: Phone `7004186276`, PIN `5524`
- Database: `crickpredict` (NOT `bharat11`)
