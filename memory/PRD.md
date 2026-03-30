# CrickPredict - Product Requirements Document

## Original Problem Statement
Fantasy Cricket Prediction App (CrickPredict) - Mobile-first PWA where users predict cricket match outcomes using virtual coins. Users answer 11 questions per match, earn points based on accuracy, compete on leaderboards.

## Tech Stack
- **Frontend:** React.js (PWA), Zustand (state), Tailwind CSS (dark theme)
- **Backend:** Python FastAPI (async)
- **Database:** MongoDB + Redis (caching/leaderboards)
- **Auth:** Phone + 4-digit PIN (no OTP), JWT tokens

## 5 Iron Rules
1. Write world's best code - stage by stage
2. Honestly judge on 50 points after stage completion
3. Optimize until ALL points reach 90+
4. Re-judge (Redis, Canonical, Optimizations)
5. Only then move to next stage

## Completed Stages

### Stage 1: Foundation (92.78%) - DONE
- FastAPI server with GZip, Request ID, Response Timing, Security Headers middleware
- MongoDB connection pooling + Redis manager
- Custom exception hierarchy + structured logging
- PWA with service worker + offline support

### Stage 2: Database (93.78%) - DONE
- 15+ Pydantic models, 9 enums, BaseRepository pattern
- Bulk IndexModel creation (compound, sparse, text)
- Idempotent seed script + bilingual models (EN/HI)

### Stage 3: Authentication (92.02%) - DONE
- Phone + 4-digit PIN auth (register/login/refresh/change-pin/me)
- bcrypt hashing, JWT access+refresh, login lockout (5 fails = 15min)
- Rate limiting (Redis + in-memory fallback)

### Stage 4: User Profile & Wallet (95.06%) - DONE
- Profile CRUD, rank progress (Rookie->GOAT), referral system
- Wallet balance, daily rewards (streak-based), transaction history
- Frontend: Profile, Wallet pages with bottom navigation

### Stage 5: Questions Bank & Templates (93.6%) - DONE
- 72+ bilingual questions across 7 categories
- Admin CRUD for questions, templates with 11 questions
- Bulk import, clone support, seed script

### Stage 6: Match Management (94.95%) - DONE
- Match CRUD, status management, template assignment
- Contest listing per match, HomePage with real match cards
- MatchDetailPage with hero card + contests

### Stage 7: Contest System (96.75%) - DONE
- Join contest: balance check, coin deduction, wallet transaction
- Duplicate prevention, lock time enforcement, max participants
- My Contests page with filters (All/Open/Live/Completed)
- MatchDetail: Join/Predict/Results buttons per contest status

### Stage 8: Prediction Submission (98.1%) - DONE
- 11 questions display (Hindi primary, English subtitle)
- Color-coded options (A/B/C/D), answer selection with highlight
- Progress bar + question dots + submit with confirmation
- Lock enforcement, pre-fill existing predictions

### Stage 9: Scoring Engine + Leaderboard (98.0%) - DONE
- Question resolution with batch scoring (idempotent)
- Contest finalization with prize distribution
- Leaderboard API (top 50 + my position)
- Full frontend integration: routing, navigation, state management

## Key Endpoints
- Auth: POST /api/auth/register, /login, /refresh, GET /me, PUT /change-pin
- User: GET/PUT /api/user/profile, /rank-progress, /referral-stats, /leaderboard
- Wallet: GET /api/wallet/balance, /transactions, POST /claim-daily
- Admin: CRUD /api/admin/questions, /templates
- Matches: GET/POST /api/matches, /{id}, /{id}/live-score, /{id}/contests
- Contests: GET/POST /api/contests, /{id}, /{id}/join, /{id}/predict, /{id}/questions
- Leaderboard: GET /api/contests/{id}/leaderboard, /leaderboard/me
- Scoring: POST /api/contests/{id}/resolve, /finalize

## Upcoming Tasks

### Stage 10: Real-time Leaderboard Polish (NEXT)
- Socket.IO for live leaderboard updates
- User detail modal (click user to see answers)
- Redis sorted sets for O(log N) operations

### Stage 11: Live Match Integration
- Cricbuzz scraping (free, 2-ball delay)
- Ball-by-ball state accumulator
- Auto-resolution triggers

### Stage 12: Result Declaration & Prize Distribution
- Auto-result when match ends
- Prize distribution to wallets
- Results UI screen

### Stage 13: Home Screen & Navigation Polish
- Pull to refresh, skeleton loading
- Match countdown timer, hot contest badges

### Stage 14: Admin Panel
- Dashboard, user management, contest management
- Live match monitor

### Stage 15: Final Polish & Deployment
- Micro-animations, performance optimization
- PWA enhancements, push notifications

## Testing Status
- Iteration 3: Backend API tests passed
- Iteration 4: Full backend tests passed
- Iteration 5: Frontend Stage 7-8-9 - 100% passed (26/26 tests)

## Progress: 60% (Stages 1-9 of 15)
