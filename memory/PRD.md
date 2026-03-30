# Bharat 11 - Product Requirements Document

## Original Problem Statement
Fantasy Cricket Prediction App ("Bharat 11") - Mobile-first PWA where users predict cricket match outcomes using virtual coins. 15-stage development with 5 Iron Rules (50-point evaluation per stage, 90+ mandatory).

## Tech Stack
- **Frontend:** React.js (PWA), Zustand, Tailwind CSS (dark theme)
- **Backend:** Python FastAPI (async)
- **Database:** MongoDB + Redis (caching/leaderboards)
- **Auth:** Phone + 4-digit PIN (no OTP), JWT tokens
- **Live Data:** pycricbuzz (Cricbuzz scraper, free, graceful fallback)

## Super Admin
- Phone: 7004186276 | PIN: 5524 | Auto-seeded on startup
- Full powers: Questions, Templates, Matches, Contests, Resolution

## Core Features Implemented

### Authentication (Stage 1-3)
- Phone + PIN login/register
- JWT access + refresh tokens
- Brute force protection (5 attempts lockout)

### User Profile & Wallet (Stage 4)
- Profile with stats, avatar, referral code
- Virtual coins economy
- Daily bonus claim

### Admin Panel (Stage 5, 13-14, NOW COMPLETE)
- **Dashboard**: Stats overview (users, questions, templates, matches, contests)
- **Questions Tab**: Full CRUD - bilingual (EN/HI), category, difficulty, points, 2-4 options
- **Templates Tab**: Create template from questions, set type (full_match/in_match), set default
- **Matches Tab**: Create match (IPL teams, venue, datetime), change status (upcoming/live/completed), assign templates (min 1 full_match, max 5)
- **Contests Tab**: Create contest (select match + template, entry fee, prize pool, max players)
- **Resolve Tab**: Resolve questions per contest, shows resolved indicator, finalize with prizes

### Template System
- **Types**: full_match (compulsory, min 1) | in_match (optional, max 4)
- **Default Templates**: If admin forgets to assign, system uses default
- **Validation**: Min 1 full_match required per match, max 5 total

### Match Management (Stage 6)
- Create matches with IPL team details
- Status transitions: upcoming -> live -> completed
- Live score updates
- Template assignment to matches
- All write endpoints require AdminUser

### Contest System (Stage 7-9)
- Join contest, make predictions
- Scoring engine with per-question points
- Leaderboard with rank, prizes
- My Contests with pagination

### Live Data (Stage 11)
- Cricbuzz scraper (pycricbuzz)
- Cache with TTL + max size limit
- Graceful fallback in container environment

### Home Page (Stage 12-13)
- Live/Upcoming/Completed match sections
- Auto-refresh every 30s
- Countdown timers
- Hot contests section

## Admin Flow (For Super Admin)
1. **Questions** -> Create bilingual questions with points and options
2. **Templates** -> Group questions into templates (1 full_match required)
3. **Matches** -> Create match, assign templates
4. **Contests** -> Create contests with entry fee/prize pool
5. **Live** -> Set match status to "live"
6. **Resolve** -> Resolve questions as match progresses
7. **Finalize** -> Distribute prizes to top players

## Honest Audits Complete (Stages 1-14)
- Stages 1-3: 4 bugs fixed (Request ID, CORS, Wallet, PIN)
- Stages 4-6: 3 bugs fixed (admin guard, status transitions)
- Stages 7-9: 3 bugs fixed (N+1 queries, pagination, finalize guard)
- Stages 10-14: 9 bugs fixed (CRITICAL match admin security, leaderboard, cache, asyncio, admin UI)

## What's NOT Yet Implemented
1. **Real-time auto-settlement** - Questions currently resolved MANUALLY by admin. No ball-by-ball auto-resolve yet.
2. **AI question generation** - Questions are manually created by admin.
3. **Stage 15: Final Polish** - PWA offline support, micro-animations, share results

## Upcoming Tasks
- Stage 15: Final PWA polish, offline support, share results
- Automated notifications for contest results
- Real-time question settlement (requires live data feed)

## Progress: 95% (14.5 of 15 stages)
