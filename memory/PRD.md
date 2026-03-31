# Bharat 11 - Fantasy Cricket Prediction PWA

## Product Requirements Document

### Original Problem Statement
Build a Fantasy Cricket Prediction PWA called "Bharat 11" with comprehensive CricketData.org API integration, AI commentary, real-time updates, admin dashboard, premium UX with world-class animations and sound effects.

### Core Architecture
- **Frontend**: React.js (PWA) + Tailwind CSS + Shadcn UI + Framer Motion + Canvas Particle Engine + Web Audio API
- **Backend**: FastAPI + Motor (async MongoDB)
- **Database**: MongoDB (`crickpredict`)
- **Real-time**: Socket.IO
- **AI**: GPT-5.2 via Emergent LLM Key
- **API**: CricketData.org (17 APIs integrated)

### What's Been Implemented

#### CricketData.org API Integration (COMPLETED)
- [x] 17 APIs integrated with strict IPL filtering and team alignment
- [x] Auto-sync startup + score normalization
- [x] Data Accuracy: 100% IPL, 0 non-IPL, 0 duplicates, 0 team swaps

#### World-Class Celebrations — Canvas Particle Engine + Sound (COMPLETED - March 31, 2026)
- [x] **Custom ParticleEngine class** — HTML5 Canvas with physics (gravity, friction, wind, wobble, rotation, trails)
- [x] **6 particle shapes** — circle, ember, stump, confetti, spark, firework
- [x] **SIX "MAXIMUM!"** — 260+ particles (120 fire embers + 80 sparks + 60 floating), golden explosion, 12 light rays, screen shake=12, "OUT OF THE PARK", 3.5s
- [x] **FOUR "BOUNDARY!"** — 270+ particles (140 electric blue embers + 60 sparks + 60 horizontal sweep + 40 ambient), 12 light rays, 3 boundary streaks, screen shake=10, "RACING TO THE FENCE", 3s
- [x] **WICKET "TIMBER!"** — 162+ particles (12 flying stumps + 100 dust debris + 50 red sparks), dark vignette, screen shake=18, slam-from-top text, 3.2s
- [x] **PRIZE "CHAMPION!"** — 300+ confetti (150+100 rain) + 3 firework bursts (120 star particles) + 40 gold sparkles, rotating conic burst, "VICTORY ROYALE", 4s
- [x] **Web Audio API Sound Effects** — Procedural synthesis, zero external files:
  - SIX: Bass hit + bat crack + crowd roar (2.5s)
  - FOUR: Bat crack + bass hit + crowd cheer (1.8s)
  - WICKET: Stumps crash + bails tinkle + crowd gasp
  - PRIZE: Victory fanfare (C5-E5-G5-C6) + sparkle shimmer + crowd eruption
- [x] **Multi-phase system** — flash → main → fadeout → dismiss
- [x] **useScreenShake hook** — RAF-based with cleanup

#### AI Commentary, WhatsApp Share Card, Auth, Admin — All complete

### Credentials
- Super Admin: Phone `7004186276`, PIN `5524`

### Remaining/Backlog Tasks
1. **P1**: Redis caching layer for hot API responses
2. **P1**: Pagination improvements (backend + frontend)
3. **P2**: 200-question pool architecture
4. **P2**: Advanced template routing (full_match vs in_match)
5. **P2**: Socket.IO live score push via Redis pub/sub
