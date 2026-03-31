# Bharat 11 - Fantasy Cricket Prediction PWA

## Product Overview
Bharat 11 is an interactive Fantasy Cricket Prediction PWA where users make ball-by-ball predictions on live IPL matches, compete in contests, earn coins, and climb leaderboards.

## Tech Stack
- **Frontend**: React.js (CRA), TailwindCSS, Framer Motion, Zustand
- **Backend**: FastAPI, MongoDB, Redis (caching)
- **Auth**: JWT (Phone + PIN based)
- **External**: CricketData.org API for live match data
- **AI**: Emergent LLM Key (GPT-5.2) for AI Ball-by-Ball commentary

## Core Features

### Authentication
- Phone + 4-digit PIN login/register
- Forgot PIN (phone-based reset)
- Change PIN (3-step flow: old PIN -> new PIN -> confirm)
- Change Username
- JWT token refresh flow
- Rate limiting & brute force protection

### User Features  
- View live/upcoming/completed matches
- Join contests and make predictions
- Dual Points Banner (Fantasy Points + Contest Coins)
- WhatsApp sharing card (Canvas rendering)
- Rank progress (Rookie -> Pro -> Expert -> Legend -> GOAT)
- Referral system with bonus coins
- Profile with stats, rank, referral code
- Prediction accuracy tracking

### Admin Features
- Match management (sync from CricketData API)
- Contest CRUD with templates/questions
- Auto Settlement Engine (AI-powered question resolution)
- Autopilot (auto match state transitions with manual override)
- User Management:
  - Search users by name/phone
  - View user details (stats, entries, predictions)
  - Ban/Unban users
  - Adjust coins (add/deduct with reason)
  - Reset user PIN
  - Filter: All / Banned
- Live ticker management
- Quick Resolve All (AI nuclear button)
- IPL Points Table management

### Performance
- Redis caching on live-ticker, matches, points-table APIs
- MongoDB compound indexes
- Pagination on all list endpoints

## Architecture
```
/app/backend/
  ├── core/ (database, security, redis_manager)
  ├── models/ (schemas.py - Pydantic models)
  ├── routers/ (auth, admin, matches, contests, user, wallet, notifications)
  ├── services/ (auth_service, user_service, cricket_data, autopilot, settlement_engine, ai_commentary, redis_cache)
  └── repositories/ (user_repository)

/app/frontend/src/
  ├── api/ (client.js - API wrapper)
  ├── components/ (auth/, ui/, CelebrationOverlay, BottomNav, etc.)
  ├── pages/ (HomePage, ProfilePage, MatchDetailPage, MyContestsPage, admin/)
  ├── stores/ (authStore, socketStore)
  └── constants/ (design.js - COLORS, RANKS, TEAM_COLORS)
```

## Implemented (as of March 31, 2026)
- [x] JWT Auth (Phone + PIN)
- [x] Match sync from CricketData API
- [x] Contest lifecycle (create -> open -> live -> completed)
- [x] Predictions system
- [x] Auto Settlement Engine
- [x] Autopilot with manual override
- [x] Redis caching
- [x] Mobile-optimized UI (360px+)
- [x] User Name Change
- [x] Change PIN (3-step flow)
- [x] Forgot PIN (phone-based reset)
- [x] Dual Points Banner (fixed total_points)
- [x] Admin User Management (search, ban/unban, coin adjust, PIN reset)
- [x] WhatsApp Sharing Card (canvas rendering)
- [x] Enhanced Profile Page
- [x] AI Ball-by-Ball Commentary (GPT-5.2)
- [x] IPL Points Table
- [x] Referral System
- [x] **Contest Status Lock**: Predictions blocked for non-live contests (only LIVE allows edit)
- [x] **Leaderboard Rank Shortcut**: Rank badge on contest cards with tap-to-navigate
- [x] **Contest Status Protocol**: LIVE=join/predict, OPEN=leaderboard only (Dream11 style), DONE=results

## Contest Status Lifecycle
- **Live**: Contest open for participation — join, submit, edit answers
- **Open**: Participation closed, match ongoing, results pending — leaderboard + user answers only
- **Done/Completed**: Match over, 100% results settled

## Backlog
### P1
- Socket.IO real-time integration for live scores
- Push notifications for match events

### P2
- Live Prediction Accuracy Leaderboard (Redis sorted sets)
- 45-second auto-polling for ball-by-ball commentary
- Heavy UI animations (six boundaries, wickets, prize winners)

### P3
- User Management tab improvements
- Tournament bracket views

## Credentials
- Super Admin: Phone: 7004186276, PIN: 5524
