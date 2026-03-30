# Bharat 11 - Product Requirements Document

## Original Problem Statement
Fantasy Cricket Prediction App ("Bharat 11") - Mobile-first PWA where users predict cricket match outcomes using virtual coins. 15-stage development. Phone + 4-digit PIN auth. Virtual coins economy.

## Tech Stack
- React.js (PWA), Zustand, Tailwind CSS (dark theme)
- FastAPI (async), MongoDB, Redis
- JWT Auth (Phone + PIN), pycricbuzz (Cricbuzz scraper)

## Super Admin: 7004186276 / PIN: 5524
- Auto-seeded on startup. 1,00,000 coins. Full admin powers.
- Gets completely separate AdminApp experience (gold-themed)

## Architecture: Complete Admin/Player Separation

### Admin Experience (is_admin=true)
- **AdminApp**: Gold-themed header with Shield icon + "Super Admin" label
- **Bottom Nav**: Dashboard | Content | Matches | Resolve
- **Dashboard**: Stats grid, live alerts, quick actions, workflow guide
- **Content Tab**: Questions CRUD + Templates CRUD (sub-tabs)
- **Matches Tab**: Match creation/status + Contest creation (sub-tabs)
- **Resolve Tab**: Per-contest resolution, progress bar, finalize
- **View as Player**: Toggle to see player experience, floating back button

### Player Experience (is_admin=false)
- **PlayerApp**: Blue-themed header "BHARAT 11"
- **Bottom Nav**: Home | My Contests | Wallet | Profile
- **ZERO admin traces**: No admin buttons, routes, or references
- Profile shows only: username, stats, referral, logout

## Auth Flow
1. Phone input → POST /api/auth/check-phone
2. If exists → Login PIN screen
3. If new → Create PIN → Confirm PIN → Register

## Template System
- Types: full_match (compulsory, min 1) | in_match (optional, max 4)
- Default template auto-assign if admin forgets
- Max 5 templates per match

## Completed Stages (14 of 15)
- Stages 1-14 implemented with honest 50-parameter audits
- 18+ real bugs found and fixed across all audits
- Complete admin panel with full CRUD for Questions, Templates, Matches, Contests
- Admin/Player complete separation at App.js level

## What's NOT Yet Implemented
1. Real-time auto-settlement (questions resolved manually by admin)
2. AI question generation
3. Stage 15: Final PWA polish (offline, micro-animations, share results)

## Upcoming: Stage 15 - Final Polish
- PWA offline support
- Share contest results
- Performance optimization

## Progress: 95% (14.5 of 15 stages)
