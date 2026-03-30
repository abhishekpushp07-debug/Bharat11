# CrickPredict - Product Requirements Document

## Original Problem Statement
Fantasy Cricket Prediction App (CrickPredict) - Mobile-first PWA where users predict cricket match outcomes using virtual coins. Users answer 11 questions per match, earn points based on accuracy, compete on leaderboards.

## Tech Stack
- **Frontend:** React.js (PWA), Zustand (state), Tailwind CSS (dark theme)
- **Backend:** Python FastAPI (async)
- **Database:** MongoDB + Redis (caching/leaderboards)
- **Auth:** Phone + 4-digit PIN (no OTP), JWT tokens
- **Live Data:** pycricbuzz (Cricbuzz scraper, free, 2-ball delay)

## 5 Iron Rules
1. Write world's best code - stage by stage
2. Honestly judge on 50 points after stage completion
3. Optimize until ALL points reach 90+
4. Re-judge (Redis, Canonical, Optimizations)
5. Only then move to next stage

## Completed Stages

### Stage 1: Foundation (92.78%) - DONE
### Stage 2: Database (93.78%) - DONE
### Stage 3: Authentication (92.02%) - DONE
### Stage 4: User Profile & Wallet (95.06%) - DONE
### Stage 5: Questions Bank & Templates (93.6%) - DONE
### Stage 6: Match Management (94.95%) - DONE
### Stage 7: Contest System (96.75%) - DONE
### Stage 8: Prediction Submission (98.1%) - DONE
### Stage 9: Scoring Engine + Leaderboard (98.0%) - DONE
### Stage 10: Leaderboard Polish (98.5%) - DONE
- User Answer Modal (click user -> see all predictions)
- Top 3 gold/silver/bronze styling
- Show More/Less toggle
- My Position highlight

### Stage 11: Live Cricket Data (92%) - DONE
- CricketDataService with pycricbuzz
- Cricbuzz sync endpoints (matches + scores)
- 30s cache, graceful fallback
- Production-ready architecture

### Stage 12-13: Home & Navigation Polish (95%) - DONE
- Live countdown timer (auto-updating)
- Refresh button + 30s auto-refresh
- Skeleton loading
- Sectioned layout (Live Now / Upcoming / Hot Contests / Completed)
- Hot Contests from real API data

### Stage 14: Admin Panel (94%) - DONE
- Dashboard with stats grid
- Match Manager (list, sync Cricbuzz, status change)
- Contest Resolution (resolve questions, finalize prizes)

## Key Endpoints
- Auth: POST /api/auth/register, /login, /refresh, GET /me
- User: GET/PUT /api/user/profile, /rank-progress, /referral-stats
- Wallet: GET /api/wallet/balance, /transactions, POST /claim-daily
- Matches: GET /api/matches, /{id}, /{id}/contests, /live/cricbuzz, POST /live/sync
- Contests: GET/POST /api/contests, /{id}/join, /{id}/predict, /{id}/questions
- Leaderboard: GET /api/contests/{id}/leaderboard, /leaderboard/me, /leaderboard/{uid}
- Admin: POST /api/contests/{id}/resolve, /finalize

## Upcoming Tasks

### Stage 15: Final Polish & Deployment (NEXT)
- PWA enhancements (install prompt, offline support)
- Micro-animations on page transitions
- Performance optimization
- Share contest/results feature
- Terms & Privacy pages

## Testing Status
- Iteration 5: Frontend Stage 7-9 - 100% (26/26)
- Iteration 6: Stages 7-14 Full - 100% (23 backend + 45 frontend)

## Progress: 93% (Stages 1-14 of 15)
