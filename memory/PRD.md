# CrickPredict - Product Requirements Document

## Project Overview
**App Name:** CrickPredict  
**Type:** Fantasy Cricket Prediction PWA  
**Tech Stack:** React.js + FastAPI + MongoDB + Redis  
**Platform:** Mobile-first PWA (installable via Chrome)

## Core Concept
Users predict cricket match outcomes by answering 11 questions per match. Virtual coins are wagered and won based on prediction accuracy.

## User Personas

### Primary: Cricket Enthusiast (18-35)
- Watches IPL/cricket matches regularly
- Enjoys fantasy sports but finds Dream11 complex
- Prefers Hindi interface
- Uses mobile primarily

### Secondary: Casual Gamer
- Likes simple prediction games
- Motivated by leaderboards and competition
- Social - shares with friends

## Core Requirements (Static)

### Authentication
- Phone + 4-digit PIN (No OTP)
- 10,000 signup bonus coins
- Referral system with bonus

### Matches & Contests
- Live cricket match integration
- Multiple contest types (Free, Mini, Mega)
- 11 questions per contest
- Real-time leaderboards

### Scoring Engine
- Ball-by-ball score integration
- Auto question resolution
- Batch score calculation
- Redis-based leaderboards

### Wallet System
- Virtual coins only
- Daily rewards with streak bonus
- Transaction history

---

## What's Been Implemented

### Stage 1: Foundation (Date: 2026-03-29) ✅
- [x] Modular backend architecture
- [x] MongoDB connection with pooling
- [x] Redis Manager for leaderboards
- [x] PWA configuration
- [x] Service worker
- [x] Zustand state management
- [x] API client with interceptors
- [x] Custom exception handling
- [x] Health check endpoints
- **Score: 47.75/50 (95.5%)**

### Stage 2: Database Schema (Date: 2026-03-29) ✅
- [x] User repository
- [x] Match repository
- [x] Contest repository
- [x] Contest entry repository
- [x] Question & Template repositories
- [x] Wallet transaction repository
- [x] Question result repository
- [x] Database seeder (12 questions, 3 matches)
- **Score: 47.6/50 (95.2%)**

### Stage 3: Authentication (Date: 2026-03-29) ✅
- [x] Registration (phone + PIN)
- [x] Login with lockout
- [x] JWT tokens (7-day expiry)
- [x] Welcome screen UI
- [x] Phone input screen
- [x] PIN screens (create/confirm/login)
- [x] Auth flow integration
- [x] Home screen after login
- **Score: 47.35/50 (94.7%)**

---

## Prioritized Backlog

### P0 - Critical (Next)
- [ ] Stage 4: User Profile & Wallet System
- [ ] Stage 5: Questions Bank & Templates (Admin)
- [ ] Stage 6: Match Management System

### P1 - High Priority
- [ ] Stage 7: Contest System
- [ ] Stage 8: Prediction Submission
- [ ] Stage 9: Scoring Engine

### P2 - Medium Priority
- [ ] Stage 10: Real-time Leaderboard
- [ ] Stage 11: Live Match Integration
- [ ] Stage 12: Result & Prize Distribution

### P3 - Lower Priority
- [ ] Stage 13: Home & Navigation Polish
- [ ] Stage 14: Admin Panel
- [ ] Stage 15: Polish & Deployment

---

## Next Tasks

### Stage 4: User Profile & Wallet System
1. Profile API (view/update)
2. Avatar selection
3. Rank system display
4. Wallet balance API
5. Transaction history
6. Daily reward claim
7. Referral code sharing
8. Profile screen UI
9. Wallet screen UI

---

## Technical Notes

### Cricket Score Integration
- Using Cricbuzz scraping (FREE)
- 2-3 ball delay acceptable
- No paid API required

### AI Integration
- GPT-5.2 via Emergent LLM Key
- For question generation
- Admin feature

### 5 Iron Rules
1. World's best code - stage wise
2. Honest 50-point judgment
3. All points reach 90%+
4. Re-judge after optimization
5. Then move to next stage

---

## Current Status
**Stage:** 3 of 15 Complete  
**Overall Progress:** 20%  
**Cumulative Score:** 47.57/50 (95.13%)
