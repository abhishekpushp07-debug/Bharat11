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

### Stage 1: Foundation (DONE - 92.78%)
- FastAPI server with lifespan management
- GZip compression, Request ID, Response timing middleware
- MongoDB connection pooling (50 max, 5 min)
- Redis manager with sorted sets, caching, rate limiting, pub/sub
- Custom exception hierarchy
- Structured logging with colored output
- PWA setup with service worker and offline support
- Zustand stores (auth, app, socket)
- API client with interceptors

### Stage 2: Database Schema & Models (DONE - 93.78%)
- 15+ Pydantic canonical models with full validation
- 9 enums for status fields
- Repository pattern (BaseRepository + 6 specialized)
- Bulk index creation (compound, sparse, text indexes)
- Idempotent seed script with --force flag
- Bilingual question models (EN/HI)

### Stage 3: Authentication (DONE - 92.02%)
- Phone + 4-digit PIN auth (register/login/refresh/change-pin/me)
- bcrypt PIN hashing
- JWT access (7d) + refresh (30d) tokens
- Login lockout (5 fails = 15min lock)
- Rate limiting on auth endpoints (Redis + in-memory fallback)
- Frontend auth flow (Welcome -> Phone -> PIN screens)

## Deep Audit Completed (2026-03-29)
- 50 parameters x 100 marks per stage = 5000 marks each
- Stage 1: 4639/5000 (92.78%)
- Stage 2: 4689/5000 (93.78%)
- Stage 3: 4601/5000 (92.02%)
- Combined: 13929/15000 (92.86%)
- Document: /app/DEEP_AUDIT_STAGE_1_2_3.md

### Optimizations Implemented in Audit:
1. GZip compression middleware (500+ bytes)
2. Request ID middleware (X-Request-ID)
3. Response timing middleware (X-Response-Time + slow request logging)
4. Moved inline imports to top-level (redis_manager, database)
5. JWT_SECRET_KEY fail-fast (no default)
6. Removed dead code (ChangePinRequest class)
7. Rate limiting on auth endpoints
8. Bulk index creation (IndexModel pattern)
9. Compound index on contest_entries(contest_id, total_points DESC)
10. TEXT index on users.username
11. Leaderboard TTL method
12. In-memory rate limit fallback when Redis down
13. Idempotent seed script (check before insert, --force flag)

## Upcoming Tasks

### Stage 4: Core Application (NEXT)
- Live match data fetching (Cricbuzz scraping - free, 2 balls late OK)
- Match listing API + UI
- Match detail page
- Live score display

### Stage 5-15: Future Roadmap
- Stage 5: Contest System
- Stage 6: Question Templates & Auto-assign
- Stage 7: Prediction Entry Flow
- Stage 8: Scoring Engine (deterministic, idempotent)
- Stage 9: Leaderboard (Redis Sorted Sets)
- Stage 10: Wallet System (Virtual Coins)
- Stage 11: User Profile & Stats
- Stage 12: Admin Panel
- Stage 13: Push Notifications
- Stage 14: Performance & Security Hardening
- Stage 15: Final Polish & Launch

## Key Design References
- Dark theme primary (black/dark grey backgrounds)
- Red accent color (#E53E3E or similar)
- Gradient cards for live matches
- Bottom navigation: Home / My Contest / Wallet / Legal
- Custom team-inspired logos (no official IPL logos)

## Progress: 20% (Stages 1-3 of 15)
