# Bharat 11 — Fantasy Cricket Prediction PWA

## Product Overview
A mobile-first PWA for fantasy cricket predictions (IPL T20). Users predict match outcomes via bilingual (Hindi/English) questions, compete in contests, and earn points.

## Core Architecture
- **Frontend**: React.js PWA (port 3000)
- **Backend**: FastAPI (port 8001, prefix `/api`)
- **Database**: MongoDB (via MONGO_URL)
- **Real-time**: Socket.IO (partially integrated)
- **AI**: OpenAI/Claude via Emergent LLM Key (Ball-by-ball commentary)
- **Cricket Data**: CricketData.org API (live scores, scorecards)

## Implemented Features (as of March 31, 2026)

### Auth & Users
- JWT auth with phone + 4-digit PIN
- Admin/Player roles
- Wallet system (deposit, withdrawal, transactions)

### Match System
- Auto-sync from CricketData API (IPL 2025 schedule)
- Match lifecycle: upcoming -> live -> completed
- Scorecard polling (45s cache)
- AI Ball-by-ball commentary (40s TTL)

### Question Pool
- 94 bilingual questions (Hindi + English)
- Categories: batting, bowling, powerplay, death_overs, match, player_performance, special
- Difficulty levels: easy (55pts), medium (70pts), hard (90pts)
- Auto-resolution rules per question (range_match, boolean_match, exact_match)

### Templates & Contests
- 5-template system per match (1 full_match + 4 in_match)
- Auto-template generation via Match Engine
- Contest creation with entry fees and prize pools
- Auto-settlement engine (45s polling)

### Admin Dashboard
- **Auto-Pilot Toggle**: START/STOP autopilot system (auto-resolve, auto-finalize, auto-create)
- **Match Auto-Engine**: One-tap actions — Seed Questions, Auto Templates All, Auto Contests 24h
- **Per-Match Controls**: Auto 5 Templates, Make Live/Unlive, Add Contest, AI Resolve
- Stats dashboard, user management, content management

### UX/Animations
- Global celebration overlay (Four/Six/Wicket animations at root level)
- Dark theme with gold accents
- Mobile-first responsive design

## Credentials
- Super Admin: Phone: 7004186276, PIN: 5524

## Tech Stack
- React.js, FastAPI, MongoDB, Socket.IO (ASGI), Pydantic
- Redis (optional, gracefully bypassed if unavailable)
- CricketData.org API, Emergent LLM Key (OpenAI/Claude)

## Upcoming Tasks (Priority Order)
1. **P1**: Socket.IO Frontend Integration (replace 30s polling)
2. **P1**: Push Notifications for match events
3. **P2**: Live Prediction Accuracy Leaderboard (Redis sorted sets)
4. **P2**: Additional heavy UI animations (prize winners, rank ups)
5. **P2**: WhatsApp sharing (HTML-to-Canvas card generation)
6. **P3**: User Management improvements
