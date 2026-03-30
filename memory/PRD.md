# Bharat 11 - Product Requirements Document

## Original Problem Statement
Fantasy Cricket Prediction PWA (IPL-only). "World's Best" standard with zero compromises. Complete architectural separation between Admin Dashboard and Player App. Auto-pipeline: Live match syncing, auto-contest creation, and real-time auto-settlement. Virtual Economy with 1 Lakh signup bonus. Dual-source live data: Cricbuzz (Primary Scraper) + CricketData.org Premium API (Scorecard + Squad).

## Architecture
- Frontend: React PWA (Tailwind CSS, Zustand, Shadcn/UI)
- Backend: FastAPI + MongoDB
- Data: BeautifulSoup4 Cricbuzz Scraper + CricketData.org Premium API
- Auth: Phone + PIN JWT auth with role-based routing

## What's Implemented (as of 2026-03-30)

### Stages 1-14: Complete
- JWT Auth (Phone+PIN), role-based routing
- Admin Dashboard (Dashboard, Content, Matches, Resolve)
- Player View (zero admin traces)
- Template system (full_match/in_match, default, editable)
- Contest system with dynamic prize pools
- Economy system (1L signup, 1000 entry, 50/30/20 prize split)
- Dual-source data fetching (Cricbuzz BS4 + CricketData.org API)
- Auto-contest creation on match sync

### Auto-Settlement Engine (Layers 3 & 4) - DONE
- CricketData.org Premium Scorecard API integration
- Scorecard parser: 40+ metrics per match
- Question auto_resolution: metric + trigger + resolution_type (range/text_match/boolean)
- 11 seeded auto-resolvable T20 questions + default template
- Auto-link CricketData IDs by team name matching
- Auto-resolve questions + auto-finalize contests + auto-distribute prizes
- Admin Resolve page: Auto-Settle + Manual tabs + Settlement Report
- Testing: 100% pass (iteration_18)

### Enhanced Features (2026-03-30) - DONE
1. **IPL-Only Filter**: Sync only fetches IPL matches (team name + series check)
2. **Rich Scorecard Display**: ScorecardView component shows batting/bowling/catching/extras per innings (20+ stats)
3. **Auto-Pilot Mode**: 45-second polling loop. Start/Stop via admin. Auto-checks live matches, evaluates questions, auto-resolves & auto-finalizes.
4. **One-Click Template**: Button to create template with all auto-resolution questions
5. **Template Editing**: Full CRUD, add/remove questions from any template (auto or manual)
6. **Enhanced Questions**: Full form with EN+HI text, 2-4 options with min/max ranges, points, auto-resolution config (metric/trigger/type)
7. **API Rate Limit Handling**: Graceful 429 errors, usage tracking
- Testing: 100% pass (iteration_19, 17/17 backend + all frontend)

### 200-Question Pool + 5-Template Auto-Engine (2026-03-30) - DONE
1. **200-Question Pool**: Seeded 200 bilingual T20 prediction questions across 7 categories (batting:40, bowling:35, powerplay:25, death_overs:25, match:30, player_performance:25, special:20). Each question has EN+HI text, 4 options with min/max ranges, auto_resolution config.
2. **Template Schema Upgrade**: Added in-match routing fields to Template model: `innings_range`, `over_start`, `over_end`, `answer_deadline_over`, `phase_label`.
3. **5-Template Auto-Engine**: Auto-generates 5 templates per match:
   - Full Match Predictions (15 questions, match_end + toss triggers)
   - Innings 1 Powerplay (10 questions, overs 1-6)
   - Innings 1 Death Overs (10 questions, overs 16-20)
   - Innings 2 Powerplay (8-10 questions, overs 1-6)
   - Innings 2 Death Overs (10 questions, overs 16-20)
4. **Admin UI**: Seed 200 button, Auto 5 Templates button per match, In-Match Routing Config in template form.
5. **Idempotent**: Both seed and auto-template endpoints skip if data already exists.
- Testing: 100% pass (iteration_20, 8/8 backend + 16/16 frontend)

## Key API Endpoints

### Auth
- POST /api/auth/check-phone, /api/auth/register, /api/auth/login

### Admin Settlement
- POST /api/admin/settlement/{match_id}/run
- GET /api/admin/settlement/status
- GET /api/admin/settlement/{match_id}/metrics
- POST /api/admin/settlement/{match_id}/link
- POST /api/admin/questions/bulk-import-with-auto

### Auto-Pilot
- POST /api/admin/autopilot/start
- POST /api/admin/autopilot/stop
- GET /api/admin/autopilot/status

### Scorecard
- GET /api/admin/scorecard/{match_id}
- GET /api/matches/{match_id}/scorecard (public)

### Matches & Contests
- POST /api/matches/live/sync (IPL-only default)
- GET/POST /api/contests, /api/admin/contests
- POST /api/contests/{id}/resolve, /api/contests/{id}/finalize

### Questions & Templates
- CRUD /api/admin/questions (with auto_resolution, min/max on options)
- CRUD /api/admin/templates (with one-click create, edit add/remove questions)
- POST /api/admin/seed-200-questions (idempotent seed)
- POST /api/admin/matches/{match_id}/auto-templates (5-template auto-engine)
- POST /api/admin/auto-templates-all (bulk auto-template for all upcoming matches)

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

### P2 - Final PWA Polish
- PWA manifest tuning, offline caching, service worker
- Performance optimization, Lighthouse audit

### P2 - Notifications
- WebSocket/Push notifications for results & prize alerts

### P2 - User Management
- Ban/Unban users, coin adjustment, activity monitoring

## Progress: 98%
