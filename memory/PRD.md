# Bharat 11 - Fantasy Cricket Prediction PWA

## Product Requirements Document

### Original Problem Statement
Build a Fantasy Cricket Prediction PWA called "Bharat 11" with comprehensive CricketData.org API integration, AI commentary, real-time updates, admin dashboard, premium UX with world-class animations.

### Core Architecture
- **Frontend**: React.js (PWA) + Tailwind CSS + Shadcn UI + Framer Motion + Canvas Particle Engine
- **Backend**: FastAPI + Motor (async MongoDB)
- **Database**: MongoDB (`crickpredict`)
- **Real-time**: Socket.IO
- **AI**: GPT-5.2 via Emergent LLM Key
- **API**: CricketData.org (17 APIs integrated)

### What's Been Implemented

#### CricketData.org API Integration (COMPLETED)
- [x] 17 APIs integrated: series_info, match_scorecard, match_info, series_points, series_squad, cricScore, match_points, match_bbb, player_info, currentMatches
- [x] Auto-sync startup + score fetching for completed matches
- [x] MongoDB indexes for performance

#### Data Accuracy System (COMPLETED - March 31, 2026)
- [x] `_align_team_info()` — Fixes random teamInfo[] swap
- [x] `_is_strictly_ipl()` — 10-team whitelist, zero non-IPL leakage
- [x] `_normalize_score()` — Both r/w/o AND runs/wickets/overs in every score
- [x] Score protection, duplicate prevention, false live detection fix
- [x] match_winner populated, series_info cache TTL
- [x] Result: 70 matches, 100% IPL, 0 duplicates, 0 swaps

#### World-Class UI Animations — Canvas Particle Engine (COMPLETED - March 31, 2026)
- [x] **Custom ParticleEngine class** — HTML5 Canvas rendering with physics (gravity, friction, wind, wobble, rotation)
- [x] **6 particle shapes** — circle, ember, stump, confetti, spark, firework (with trails, glow, shadows)
- [x] **SIX "MAXIMUM!"** — 200+ fire embers in 3 waves, golden explosion, light rays, 12 radiating beams, screen shake (12), "OUT OF THE PARK" subtitle, 3.5s duration
- [x] **FOUR "BOUNDARY!"** — 120 blue wave particles, 3 neon boundary streaks, horizontal momentum slide text, "RACING AWAY" subtitle, 2.8s duration
- [x] **WICKET "TIMBER!"** — 12 flying stump pieces, 100 dust/debris, 50 red sparks, dark vignette, screen shake (18 — heaviest), slam-from-top text with impact bounce, 3.2s duration
- [x] **PRIZE "CHAMPION!"** — 300 confetti rain in 2 waves, 3 firework bursts at different positions (40 star particles each), 40 gold sparkles, rotating conic light burst, "VICTORY ROYALE" subtitle, 4s duration
- [x] **ShockwaveRings** — 4 SVG expanding rings per celebration
- [x] **useScreenShake hook** — requestAnimationFrame-based with proper cleanup (no memory leaks)
- [x] **Multi-phase system** — flash (0.15s) → main → fadeout (0.5s) → dismiss
- [x] **Demo trigger strip** — 4 buttons on Match Detail page for testing all celebrations
- [x] **Match card staggered entry** — Framer Motion slide-up with per-card delay
- [x] **Winner text slide animation** — Completed match results animate in from left
- [x] **Event badge glow effects** — CSS keyframes: sixBadgeGlow, wicketBadgePulse, fourSweep

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
