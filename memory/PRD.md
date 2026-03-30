# Bharat 11 - Product Requirements Document

## Original Problem Statement
Fantasy Cricket Prediction PWA with 15-stage strict development plan. "World's Best" standard with zero compromises. Complete architectural separation between Admin Dashboard and Player App. Auto-pipeline: Live match syncing, auto-contest creation, and real-time auto-settlement. Virtual Economy with 1 Lakh signup bonus. Dual-source live data: Cricbuzz (Primary Scraper) + CricketData.org (Fallback API).

## Architecture
- Frontend: React PWA (Tailwind CSS, Zustand, Shadcn/UI)
- Backend: FastAPI + MongoDB
- Data: BeautifulSoup4 Cricbuzz Scraper + CricketData.org Premium API (Scorecard + Squad)
- Auth: Phone + PIN JWT auth with role-based routing

## Core Requirements
1. 15-stage development plan with honest audits
2. Admin/Player complete separation (zero admin traces in player UI)
3. Auto Pipeline: Live Match Sync -> Auto Contest Creation -> Auto Settlement -> Auto Prize Distribution
4. Virtual Economy: 1L signup, 1000 entry, 50/30/20 prize split
5. Dual-source data: Cricbuzz scraping + CricketData.org API

## Key Features Implemented
### Stages 1-14: Complete
- JWT Auth (Phone+PIN), role-based routing
- Admin Dashboard (Dashboard, Content, Matches, Resolve tabs)
- Player View (completely separated)
- Template system (full_match/in_match, default templates)
- Contest system with dynamic prize pools
- Economy system (coins, wallet, transactions)
- Dual-source data fetching (Cricbuzz BS4 + CricketData.org API)
- Auto-contest creation on match sync

### Auto-Settlement Engine (Layer 3 & 4) - COMPLETED 2026-03-30
- CricketData.org Premium Scorecard API integration
- Scorecard parser extracts 40+ metrics per match (innings runs, wickets, sixes, fours, extras, run rate, highest scorer, best bowler, etc.)
- Question auto_resolution config: metric + trigger + resolution_type (range/text_match/boolean)
- Seeded 11 auto-resolvable T20 questions with default template
- Auto-link CricketData.org match IDs by team name matching
- Auto-resolve questions when trigger conditions met
- Auto-finalize contests and distribute prizes (50/30/20)
- Admin UI: Manual Resolve + Auto-Settle tabs
- Settlement Report: shows key metrics, contest progress, finalization status
- Testing: 100% pass rate (iteration_18)

## API Endpoints
### Auth
- POST /api/auth/check-phone
- POST /api/auth/register
- POST /api/auth/login

### Admin Settlement (NEW)
- POST /api/admin/settlement/{match_id}/run - Run auto-settlement
- GET /api/admin/settlement/status - Get all matches settlement status
- GET /api/admin/settlement/{match_id}/metrics - Parsed scorecard metrics
- GET /api/admin/settlement/{match_id}/scorecard - Raw scorecard data
- POST /api/admin/settlement/{match_id}/link - Link CricketData.org ID
- POST /api/admin/questions/bulk-import-with-auto - Seed 11 auto-resolution questions

### Matches & Contests
- POST /api/matches/live/sync - Sync live matches
- GET /api/contests, POST /api/admin/contests
- POST /api/contests/{id}/resolve, /api/contests/{id}/finalize

## Backlog
### P1 - Stage 15: Final Polish & Launch
- PWA manifest tuning, offline caching, service worker
- Performance optimization, lighthouse audit
- Deployment prep

### P2 - Notifications
- WebSocket/Push notifications for contest results
- Prize distribution alerts

### P2 - User Management
- Admin tab for Ban/Unban users
- Coin balance adjustment
- User activity monitoring

## Progress: 97%
