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
- [x] Data Accuracy: 100% IPL, 0 non-IPL, 0 duplicates, 0 team swaps

#### World-Class Celebrations — Canvas Particle Engine + Sound (COMPLETED)
- [x] SIX: 260+ fire embers, golden explosion, crowd roar sound
- [x] FOUR: 270+ electric blue particles, boundary streaks, bat crack sound
- [x] WICKET: Flying stumps, dust debris, stumps crash sound
- [x] PRIZE: 300 confetti, firework bursts, victory fanfare sound

#### Question Pool & Templates (COMPLETED - March 31, 2026)
- [x] **16 questions seeded** (bilingual Hindi+English)
- [x] **Difficulty-based points**: Easy=55, Medium=70, Hard=90
- [x] **Distribution**: 2 Easy, 5 Medium, 9 Hard
- [x] **2 Templates**:
  - First Innings (in_match): 4 questions, 305 pts — runs, wickets, sixes, fours
  - Full Match (full_match): 12 questions, 965 pts — winner, death overs, player performance, extras, century
- [x] **Evaluation rules**: range_match (with min/max), boolean_match (threshold), exact_match
- [x] **Categories**: batting, bowling, match, death_overs, player_performance, special
- [x] **Total Points**: 1270 across both templates

#### AI Commentary, WhatsApp Share Card, Auth, Admin — All complete

### Credentials
- Super Admin: Phone `7004186276`, PIN `5524`

### Remaining/Backlog Tasks
1. **P1**: Redis caching layer for hot API responses
2. **P1**: Pagination improvements (backend + frontend)
3. **P2**: Auto-settlement engine for seeded questions
4. **P2**: Socket.IO live score push via Redis pub/sub
