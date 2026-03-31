# Bharat 11 - Fantasy Cricket Prediction PWA

## Product Requirements Document

### Original Problem Statement
Build a Fantasy Cricket Prediction PWA called "Bharat 11" with comprehensive CricketData.org API integration, AI commentary, real-time updates, admin dashboard, premium UX with world-class animations.

### Core Architecture
- **Frontend**: React.js (PWA) + Tailwind CSS + Shadcn UI + Framer Motion
- **Backend**: FastAPI + Motor (async MongoDB)
- **Database**: MongoDB (`crickpredict`)
- **Real-time**: Socket.IO
- **AI**: GPT-5.2 via Emergent LLM Key
- **API**: CricketData.org (17 APIs integrated)

### What's Been Implemented

#### CricketData.org API Integration (COMPLETED)
- [x] series_info — 70 IPL matches synced, auto-sync on startup
- [x] match_scorecard, match_info, series_points, series_squad
- [x] cricScore, match_points, match_bbb, player_info
- [x] Auto-sync startup + score fetching for completed matches
- [x] MongoDB indexes — api_cache (compound unique), matches.cricketdata_id (sparse)

#### Data Accuracy System (COMPLETED - March 31, 2026)
- [x] `_align_team_info()` — Fixes random teamInfo[] swap
- [x] `_is_strictly_ipl()` — 10-team whitelist, zero non-IPL leakage
- [x] `_normalize_score()` — Both r/w/o AND runs/wickets/overs in every score
- [x] Score protection, duplicate prevention, false live detection fix
- [x] match_winner populated, series_info cache TTL
- [x] Result: 70 matches, 100% IPL, 0 duplicates, 0 swaps

#### World-Class UI Animations (COMPLETED - March 31, 2026)
- [x] **SIX Celebration** — Fiery golden explosion, 50 radial particles, 3 shock rings, "MAXIMUM!" text with fire gradient, screen flash, ambient glow
- [x] **FOUR Celebration** — Neon blue boundary streak, horizontal sweep, "BOUNDARY!" text with skew slide-in
- [x] **WICKET Celebration** — 3 flying stumps + 2 bails, dark red flash, "WICKET!" slam from top with screen shake
- [x] **PRIZE/WINNER Celebration** — 60 gold confetti pieces, rotating conic light burst, "WINNER!" bounce-in
- [x] **Match Card Staggered Entry** — Framer Motion slide-up with delay per card
- [x] **Winner Text Animation** — Slide-in from left for completed match results
- [x] **Event Badge Glow Effects** — sixBadgeGlow, wicketBadgePulse, fourBadgeSweep CSS animations
- [x] **Demo Trigger Strip** — 4 buttons on Match Detail page to test all celebrations
- [x] **AnimatedScore Component** — Live score number transitions with glow pulse (created but available for future live integration)

#### AI Commentary (COMPLETED)
- [x] 4-tab system: Match Story, Phase Analysis, Timeline, MVPs

#### WhatsApp Share Card (COMPLETED)

#### Auth, Matches, Contests, Admin, UX — All complete

### Credentials
- Super Admin: Phone `7004186276`, PIN `5524`

### Remaining/Backlog Tasks
1. **P1**: Redis caching layer for hot API responses
2. **P1**: Pagination improvements (backend + frontend)
3. **P2**: 200-question pool architecture
4. **P2**: Advanced template routing (full_match vs in_match)
5. **P2**: Socket.IO live score push via Redis pub/sub
