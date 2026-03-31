# Bharat 11 - Fantasy Cricket Prediction PWA

## Product Overview
Fantasy Cricket Prediction PWA with JWT auth, real-time Socket.IO, push notifications, comprehensive Super Admin panel, and world-class IPL Encyclopedia with 115+ verified records.

## Architecture
- **Frontend**: React.js PWA (mobile-first, dark theme)
- **Backend**: FastAPI + MongoDB (`crickpredict` DB)
- **Real-Time**: python-socketio (ASGI)
- **API Cache**: Custom caching layer for CricketData API

## What's Been Implemented

### Core Platform (DONE)
- JWT Auth (phone + PIN), Match sync, Contest CRUD, 567 bilingual questions
- Template system (Full Match / In-Match), Auto-settlement engine (45s polling)
- Socket.IO real-time, Push notifications (VAPID), API caching, Prediction streaks

### Super Admin Overhaul (DONE)
- Bulk Delete, Default Templates (5 slots), AI Override Resolve, Quick Resolve All
- Template Type Badges, Manual Contest Creation, Player View toggle

### IPL Encyclopedia - World's Most Comprehensive (DONE - March 31, 2026)

#### 115+ Real Verified Records across 8 Categories:
- **Batting (25)**: Most Runs (Kohli 8,661), Highest Score (Gayle 175*), Fastest Century (30 balls), Fastest Fifty (Jaiswal 13 balls), Most Sixes (Gayle 357), Most Fours (Kohli 772), Most Centuries (Kohli 8), Highest Partnership (Kohli-ABD 229), etc.
- **Bowling (15)**: Most Wickets (Chahal 221), Best Figures (Alzarri Joseph 6/12), Best Economy (Narine 6.81), Most Hat-tricks (Amit Mishra 3), Most Purple Caps (Bhuvi & Harshal 2), etc.
- **Fielding (8)**: Most Catches Fielder (Kohli 117), Most WK Dismissals (Dhoni 201), Most Stumpings (Dhoni 47), etc.
- **Team (15)**: Highest Total (SRH 287/3), Lowest Total (RCB 49), Longest Win Streak (KKR 14), MI vs CSK H2H (21-18), etc.
- **Controversy & Drama (12)**: Slapgate 2008, Spot-Fixing 2013, CSK/RR Ban 2016-17, Mankading 2019, Bio-Bubble 2021, RCB 49 All Out, CSK Comeback 2018, Double Super Over, etc.
- **Fun & Unique (12)**: Most Expensive Over (37 runs), Youngest Debut (Vaibhav Suryavanshi 14 yrs), Oldest Player (Brad Hogg 45 yrs), SRH Owns Top 3 Totals, Ee Sala Cup Namde Finally!, etc.
- **Champions (18)**: Every IPL winner 2008-2025 with final scores, stories, and iconic moments
- **Auction Milestones (10)**: Dhoni Rs 9.5 Cr (2008) to Pant Rs 27 Cr (2025), Jadeja unsold-to-star arc

#### 20 Players with Real Stats (verified from iplt20.com, ESPNcricinfo)
#### 10 Cap Winners (2016-2025)
#### Head-to-Head Comparison (animated bars, verdict)

#### All 10 Team Profiles with Rich Storytelling Histories:
- **MI**: 5 titles dynasty, two 1-run finals, Rohit mid-season captaincy, Bumrah discovery
- **CSK**: 2-year ban comeback, Watson 117* bleeding knee, Dhoni 112m six, Whistle Podu religion
- **RCB**: 17-year wait, 49 all out darkest day, Ee Sala Cup Namde prophecy, 2025 maiden title tears
- **KKR**: McCullum 158* first IPL ball, SRK's Bollywood-meets-cricket, Narine's 2024 reinvention, 14-win streak
- **DC**: 7 captains in 8 years, cursed franchise, Pant car crash comeback, 2020 first final
- **PBKS**: Eternal heartbreak, topped league twice but never won, 2025 runner-up by 6 runs, Preity Zinta screams
- **SRH**: Phoenix from Deccan Chargers ashes, bowling-first to batting monsters, owns top 3 totals
- **RR**: Shane Warne's underdog miracle 2008, spot-fixing scandal, Jaiswal's panipuri-to-stardom
- **GT**: Debut season champions 2022, world's largest stadium, both 2025 caps
- **LSG**: Rs 7,090 Cr franchise, Goenka-Rahul drama, Pant Rs 27 Cr record

## UI Features
- Tab-based record categories with count badges
- Featured record hero banner
- IPL Rhombus search button (bottom nav center)
- Dual Points banner
- Category filter horizontal scroll tabs

## Remaining Tasks
### P1
- Auto template generation (full_match/in_match intervals)
- Performance optimization / Lighthouse audit

### P2
- Heavy animations (sixes/wickets celebrations)
- WhatsApp share card confetti
- Service Worker offline page
- User Management Tab

## Key Files
- `/app/backend/services/ipl_data_seeder.py` - 115 records, 20 players, 10 caps - ALL REAL DATA
- `/app/backend/routers/ipl_router.py` - IPL search, records, players, caps, head-to-head APIs
- `/app/frontend/src/pages/SearchPage.jsx` - Tab-based records UI, teams, players, H2H
- `/app/frontend/src/components/HeadToHead.jsx` - Player comparison animated bars
- `/app/frontend/src/pages/TeamProfilePage.jsx` - Rich storytelling team profiles

## Credentials
- Super Admin: Phone `7004186276`, PIN `5524`
- Database: `crickpredict` (NOT `bharat11`)
