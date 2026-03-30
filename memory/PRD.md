# Bharat 11 - Fantasy Cricket Prediction PWA

## Product Overview
IPL-focused fantasy cricket prediction platform. Users predict match outcomes via 11-question templates (4 options each), earn virtual coins, compete on leaderboards. Real-time updates, AI-powered commentary, 100% legal under Indian gaming law.

## Core Business Logic
1. Admin adds up to 2000 questions (bilingual EN+HI) in a pool
2. Templates: max 11 questions each. Types: `full_match` or `in_match` (with innings/over range)
3. Per match: max 5 templates (1 full_match required + up to 4 in_match)
4. **Answer Deadlines:**
   - Full match: answer by 1st innings 12th over, editable until then
   - In-match 1st inn 1-12: deadline at 1st inn over 5
   - In-match 1st inn 12.1-20: deadline at 1st inn over 14.6
   - In-match 2nd inn 1-12: deadline at 2nd inn over 5
   - In-match 2nd inn 12.1-20: deadline at 2nd inn over 14.6
5. Contests auto-go-live 24hrs before match start
6. Auto-settlement: AI resolves questions from live scorecard after every ball
7. Default fallback: if no template attached, last match's template is used

## Tech Stack
React.js + FastAPI + MongoDB + Socket.IO + VAPID Push + CricketData.org API + Emergent LLM Key

## What's Implemented (All Tested 100%)

### Core Features
- JWT Auth (phone/PIN)
- Match/Contest/Template/Question CRUD (full admin panel)
- Auto-settlement engine with scorecard parsing + streak multipliers
- Auto-pilot background tasks
- Socket.IO real-time (live scores, contest events)
- Web Push Notifications (VAPID)
- Admin User Management (search, ban, coin adjust)
- AI Ball-by-ball Commentary
- Prediction Streak (Snapchat-style fire UI)
- Prediction Badge + Mood Meter
- MongoDB API Cache Layer (never fetch same data twice)
- Team Drill-Down (click team → matches → full match data)
- Legal page with 6-point Indian gaming law compliance

### Session 3 Fixes (Mar 31, 2026)
- **Hot Contests clickable** — Click story circle → navigate to match detail page
- **Hot Contests filtered** — Only shows contests for matches within 24 hours
- **Contest Questions fixed** — All 11 contests now have valid bilingual questions (question_ids remapped)
- **Question Pool expanded** — System supports up to 2000 questions. Currently 778 seeded (bilingual EN+HI)
- **Admin Questions pagination** — 100 per page with Prev/Next. Search by text, filter by category
- **Question Edit/Delete** — Full modal form with all fields (EN/HI text, category, difficulty, points, options, auto_resolution)
- **5-Template Engine NoneType fix** — Handles null auto_resolution gracefully
- **Templates remapped** — All templates now reference valid question IDs from current pool

## Key API Endpoints
- `POST /api/admin/seed-question-pool?count=2000` — Seed question pool
- `POST /api/admin/matches/{id}/auto-templates` — 5-Template Engine
- `GET /api/contests/{id}/questions` — Contest questions (bilingual)
- `GET /api/admin/questions?page=1&limit=100` — Paginated question management
- `PUT /api/admin/questions/{id}` — Edit question
- `DELETE /api/admin/questions/{id}` — Delete question

## Remaining / Backlog
### P1
- Performance optimization / Lighthouse audit
- Socket.IO connection stability
- Fantasy + Contest dual points banner on home (partial)

### P2
- WhatsApp share card confetti effects
- Heavy animations (sixes, wickets, fours visual celebrations)
- Service Worker offline page
- Final cleanup
