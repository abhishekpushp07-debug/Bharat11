# Bharat 11 - Product Requirements Document

## Original Problem Statement
Fantasy Cricket Prediction PWA (IPL-only). New type betting app where users answer 11 questions from 4 options. Questions auto-resolve from live scorecard. Dream 11 style leaderboard. "World's Best" standard.

## Hard Rules
1. App is IPL-ONLY. No other cricket series.
2. Max 200 questions in pool, each with fixed points
3. Templates from 200 questions, MAX 11 questions per template
4. Template types: full_match or in_match (with overs+innings range)
5. Max 5 templates per match (1 full + 4 in-match), min 1 full
6. Answer deadlines:
   - Full match → 1st innings 12th over (editable before)
   - In-match 1st inn 1-12 → 1st innings 5th over
   - In-match 1st inn 12.1-20 → 1st innings 14.6 over
   - In-match 2nd inn 1-12 → 2nd innings 5th over
   - In-match 2nd inn 12.1-20 → 2nd innings 14.6 over
7. Default fallback: If no template assigned → last match's templates auto-apply
8. Contests auto-live 24h before match start
9. Auto-settlement: per-ball AI agent answers from scorecard
10. Leaderboard: backend calculates right answers ONCE, matches against ALL users

## Architecture
- Frontend: React PWA (Tailwind CSS, Zustand, Shadcn/UI)
- Backend: FastAPI + MongoDB
- Data: CricketData.org Premium API (2000 calls/day) + Cricbuzz Scraper
- Auth: Phone + PIN JWT auth

## What's Implemented

### Core Infrastructure (Stages 1-14)
- JWT Auth, role-based routing (Admin/Player)
- Admin Dashboard + Player View (zero admin traces)
- Template/Contest/Question CRUD
- Economy: 1L signup, 1000 entry, 50/30/20 prize
- Auto-contest creation, auto-pilot (45s polling)

### Auto-Settlement Engine
- 40+ metrics per match from scorecard
- Question auto_resolution: metric + trigger + resolution_type
- Auto-resolve + auto-finalize + auto-distribute prizes

### Stage 1 — IPL Cleanup + Team Logos (2026-03-30) ✅
- Deleted 25 non-IPL matches + 35 non-IPL contests
- All 10 IPL team logos integrated (user-provided + CricketData API)
- Real logos in: Match cards, Ticker, Points table, Match detail hero
- Testing: 100% pass (iteration_22)

### Stage 2 — Answer Deadline Enforcement (2026-03-30) ✅
- Backend middleware checks current innings/over before accepting predictions
- Full match → locked after 1st innings 12th over
- In-match 1-12 → locked after Ov 5.0 of target innings
- In-match 12.1-20 → locked after Ov 14.6 of target innings
- GET /api/matches/{id}/template-deadlines → OPEN/LOCKED status per template
- Frontend: Deadline badges in Contests tab

### Stage 3 — Max 11 + Default Template Fallback (2026-03-30) ✅
- Max 11 questions per template enforced (backend + auto-engine)
- Default fallback: POST /api/admin/matches/{id}/apply-default-templates
- Copies last match's templates if match has none

### Stage 4 — Contest Auto-Live 24h (2026-03-30) ✅
- POST /api/admin/auto-contests-24h
- Background task in autopilot (every 10th cycle)
- Auto-creates contest with assigned/fallback templates

### Stage 5 — Points & Leaderboard (2026-03-30) ✅
- Points = correct_answer × question_points (per-question scoring)
- Backend calculates right answers ONCE, matches all users
- Leaderboard ranking by total score

### Stage 6 — Ball-by-Ball + Player Profile Modal (2026-03-30) ✅
- match_bbb API integrated (LOT4)
- Live tab with ball-by-ball commentary (wickets, fifties, centuries, bowling)
- Player Profile Modal: click player → career stats popup
- 5-tab Match Detail: Contests | Live | Scorecard | Squad | Fantasy Pts

### 200-Question Pool + 5-Template Auto-Engine ✅
- 200 bilingual T20 questions (7 categories)
- 5-template auto-engine per match (1 full + 4 in-match)

### CricketData.org API Integration (14/17 APIs used) ✅
- Points Table, Live Ticker, Squad, Fantasy Pts, Match Info, Scorecard, BBB, Player Info, Schedule, Squads

## Backlog

### P1 - Stage 7: Dual Points Banner on Home
- Fantasy Points + Contest Coins side by side

### P1 - Stage 8: Socket.IO Real-Time
- Live score push, question resolved, leaderboard update, template locked events

### P2 - Stage 9: Heavy Animations
- Six hit (golden 6 explosion), Wicket (red flash), Four (blue boundary), Prize (confetti)

### P2 - Stage 10: WhatsApp Share Card
- HTML-to-Canvas card with rank + score + match info

### P2 - Stage 11: Push Notifications + PWA Polish
- Match starting, results ready, contest won/lost notifications

### P2 - Stage 12: User Management + Final Polish
- Admin user management, performance optimization, Lighthouse audit
