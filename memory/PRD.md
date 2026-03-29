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

### Stage 1: Foundation (92.78%)
- FastAPI server with GZip, Request ID, Response Timing, Security Headers middleware
- MongoDB connection pooling + Redis manager
- Custom exception hierarchy + structured logging
- PWA with service worker + offline support

### Stage 2: Database (93.78%)
- 15+ Pydantic models, 9 enums, BaseRepository pattern
- Bulk IndexModel creation (compound, sparse, text)
- Idempotent seed script + bilingual models (EN/HI)

### Stage 3: Authentication (92.02%)
- Phone + 4-digit PIN auth (register/login/refresh/change-pin/me)
- bcrypt hashing, JWT access+refresh, login lockout (5 fails = 15min)
- Rate limiting (Redis + in-memory fallback)

### Stage 4: User Profile & Wallet (95.06%)
- Profile CRUD, rank progress (Rookie→GOAT), referral system
- Wallet balance, daily rewards (streak-based), transaction history
- Frontend: Profile, Wallet pages with bottom navigation

### Stage 5: Questions Bank & Templates
- 72+ bilingual questions across 7 categories (match_outcome, runs, wickets, boundaries, player_performance, milestone, special)
- Admin CRUD for questions (create, update, delete, bulk-import)
- 7+ templates with question linking, clone support
- Template resolution (returns questions with template)

### Stage 6: Match Management
- Match CRUD (create, list, detail, status update)
- Live score update API
- Template assignment to matches
- Contest listing per match
- Frontend: Real match cards from API, Match Detail page

## Key Endpoints
- Auth: POST /api/auth/register, /login, /refresh, GET /me, PUT /change-pin
- User: GET/PUT /api/user/profile, /rank-progress, /referral-stats, /leaderboard
- Wallet: GET /api/wallet/balance, /transactions, POST /claim-daily
- Admin: CRUD /api/admin/questions, /templates (+ bulk-import, clone)
- Matches: GET/POST /api/matches, /{id}, /{id}/live-score, /{id}/contests

## Upcoming Tasks

### Stage 7: Contest System (NEXT)
- Contest CRUD (admin creates contests per match)
- Join contest (deduct entry fee from wallet)
- Contest entry: user answers 11 questions
- My Contests page (frontend)

### Stage 8: Prediction Entry Flow
- Question display from template
- Answer submission with timer
- Answer lock before match starts

### Stage 9: Scoring Engine
- Deterministic evaluation per question
- Batch scoring: one evaluation → all users
- Redis sorted set leaderboard per contest

### Stages 10-15: Future
- Stage 10: Contest Leaderboard (Redis Sorted Sets)
- Stage 11: Live Match Integration (Cricbuzz scraping)
- Stage 12: Admin Panel UI
- Stage 13: Push Notifications
- Stage 14: Performance & Security Hardening
- Stage 15: Final Polish & Launch

## Progress: 40% (Stages 1-6 of 15)
