# Bharat 11 - Fantasy Cricket Prediction PWA

## Product Requirements Document

### Original Problem Statement
Build a Fantasy Cricket Prediction PWA called "Bharat 11" with:
- JWT-based authentication with phone + PIN
- Live match tracking with CricketData.org API
- Contest-based prediction system
- AI-powered commentary (GPT-5.2)
- Real-time updates via Socket.IO
- Admin dashboard with user management
- IPL Encyclopedia with real historical data
- WhatsApp sharing with premium card generation
- Heavy animations and cricket celebrations

### Core Architecture
- **Frontend**: React.js (PWA) with Tailwind CSS, Shadcn UI, Framer Motion
- **Backend**: FastAPI (Python) with Motor (async MongoDB)
- **Database**: MongoDB (`crickpredict`)
- **Real-time**: Socket.IO
- **AI**: GPT-5.2 via Emergent LLM Key for commentary
- **API**: CricketData.org for live match data

### What's Been Implemented

#### Authentication & Core
- [x] Phone + PIN login/register with JWT
- [x] Super Admin role system
- [x] Wallet system (virtual coins)

#### Matches & Contests
- [x] Match sync from CricketData.org
- [x] Auto-contest generation (3-tier template system)
- [x] Contest joining & prediction submission
- [x] Auto-settlement engine (45s polling)
- [x] Leaderboard with real-time updates

#### Admin Panel
- [x] Dashboard with stats overview
- [x] Match management
- [x] Template & question management
- [x] Quick Resolve (AI bulk resolution)
- [x] User management tab

#### UX Features
- [x] IPL Encyclopedia (115+ real records, head-to-head comparison)
- [x] Cricket celebrations (Six, Four, Wicket animations)
- [x] Prediction streaks with diamond theme
- [x] Mood meter (Instagram-style polls)
- [x] Player profiles with stats
- [x] Service worker offline support
- [x] React.lazy/Suspense code splitting

#### **WhatsApp Share Card (COMPLETED - March 2026)**
- [x] Premium collectible card design (Topps Chrome / NBA Top Shot aesthetic)
- [x] 9:16 portrait ratio (360x640px, 2x scale for 1080x1920)
- [x] Gold corner decorations and accent borders
- [x] Oversized rank display (#1 with 96px font, glow effects)
- [x] Bento stats grid (Points, Accuracy, Correct)
- [x] Accuracy progress bar with color coding
- [x] Mood meter integration in card
- [x] Confetti effect for top 3 finishes
- [x] html2canvas compatible (no backdrop-filter, px units only)
- [x] Share on WhatsApp + Download button
- [x] Rank labels (CHAMPION, RUNNER UP, BRONZE, WARRIOR)

#### **AI Ball-by-Ball Commentary (COMPLETED - March 2026)**
- [x] ESPN+ / Instagram Stories immersive design
- [x] 4-tab system: Match Story, Phase Analysis, Timeline, MVPs
- [x] **Match Story**: Match Pulse hero card, top 5 moments, turning point, verdict
- [x] **Phase Analysis**: Powerplay (1-6), Middle (7-15), Death (16-20) breakdown
- [x] **Momentum Indicator**: Visual bar showing batting vs bowling dominance
- [x] **Timeline View**: Vertical spine timeline with oversized over numbers
- [x] **Star Performers (MVPs)**: Player cards with ratings, role badges, animated bars
- [x] Quick stats bar (Sixes count, Wickets count, Momentum score)
- [x] Framer Motion animations throughout (stagger, slide, scale)
- [x] Event-specific styling (Six=gold, Four=blue, Wicket=red, Milestone=green)
- [x] Turning Point card with purple gradient
- [x] Verdict card with mood-based theming (thriller/domination/upset/classic/heartbreak)
- [x] Fallback to scorecard-based highlights when no AI data
- [x] Celebration trigger on tapping event badges

### Credentials
- Super Admin: Phone `7004186276`, PIN `5524`
- Database: `crickpredict`

### Tech Stack
- React.js, FastAPI, MongoDB, Socket.IO
- html2canvas, framer-motion, lucide-react
- CricketData.org API, GPT-5.2 (Emergent LLM)

### Remaining/Backlog Tasks
1. **P0**: CricketData.org API comprehensive integration (replace Cricbuzz scraping)
2. **P0**: IPL schedule bulk sync (series_info → DB)
3. **P1**: Redis caching layer for API responses
4. **P1**: MongoDB indexing for api_cache collection
5. **P1**: Pagination improvements (backend + frontend)
6. **P2**: Socket.IO live score push via Redis pub/sub
7. **P2**: 200-question pool architecture
8. **P2**: Advanced template routing (full_match vs in_match)
