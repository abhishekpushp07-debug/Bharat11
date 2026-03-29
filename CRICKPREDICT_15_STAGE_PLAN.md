# CrickPredict - 15 Stage Development Plan
## Fantasy Cricket Prediction PWA (Progressive Web App)

---

## PROJECT OVERVIEW

**App Type:** Mobile-First PWA (Progressive Web App) - Chrome/Safari installable shortcut
**Tech Stack:** React.js + Tailwind CSS + FastAPI + MongoDB + Redis
**AI Integration:** GPT-5.2 (via Emergent LLM Key) for Question Generation
**Cricket API:** EntitySport (Ball-by-ball WebSocket data)
**Authentication:** Phone Number + 4-digit PIN (No OTP)
**Economy:** Virtual Coins Only (No Real Money)

---

## 15 STAGES BREAKDOWN

---

### STAGE 1: Project Foundation & Core Setup
**Duration:** Day 1-2
**Priority:** Critical

#### Tasks:
1. **Project Structure Setup**
   - Initialize React.js PWA with service worker
   - Setup FastAPI backend with modular structure
   - Configure MongoDB connection with proper models
   - Setup Redis for leaderboards & caching

2. **PWA Configuration**
   - manifest.json for installability
   - Service worker for offline support
   - App icons (192x192, 512x512)
   - Theme colors matching dark UI

3. **Environment Configuration**
   - Backend .env (MongoDB, Redis, API keys)
   - Frontend .env (Backend URL)
   - CORS configuration

#### Deliverables:
- [ ] Running PWA shell
- [ ] Backend health check endpoint
- [ ] MongoDB & Redis connected
- [ ] PWA installable on mobile Chrome

---

### STAGE 2: Database Schema & Models
**Duration:** Day 2-3
**Priority:** Critical

#### MongoDB Collections:

```javascript
// 1. users
{
  _id: ObjectId,
  phone: String (unique, indexed),
  pin_hash: String,
  username: String,
  avatar_url: String,
  coins_balance: Number (default: 10000),
  rank_title: String (Rookie/Pro/Expert/Legend/GOAT),
  total_points: Number,
  matches_played: Number,
  contests_won: Number,
  referral_code: String (unique),
  referred_by: ObjectId,
  daily_streak: Number,
  last_daily_claim: Date,
  created_at: Date,
  updated_at: Date
}

// 2. matches
{
  _id: ObjectId,
  external_match_id: String (EntitySport ID),
  team_a: {
    name: String,
    short_name: String,
    logo_url: String
  },
  team_b: {
    name: String,
    short_name: String,
    logo_url: String
  },
  venue: String,
  match_type: String (T20/ODI/Test),
  status: String (upcoming/live/completed/abandoned),
  start_time: Date,
  toss_winner: String,
  toss_decision: String,
  live_score: Object,
  result: String,
  templates_assigned: [ObjectId],
  created_at: Date
}

// 3. questions_bank
{
  _id: ObjectId,
  question_text_en: String,
  question_text_hi: String,
  category: String (batting/bowling/match/powerplay/death_overs),
  options: [
    { key: "A", text_en: String, text_hi: String },
    { key: "B", text_en: String, text_hi: String },
    { key: "C", text_en: String, text_hi: String },
    { key: "D", text_en: String, text_hi: String }
  ],
  points: Number (default: 50-100),
  multiplier: Number (1.0/1.5/2.0),
  evaluation_rules: {
    type: String (range_match/boolean_match/compound_match/dual_range_match),
    metric: String,
    comparator: String,
    threshold: Number,
    resolution_trigger: String
  },
  difficulty: String (easy/medium/hard),
  is_active: Boolean,
  created_at: Date
}

// 4. templates
{
  _id: ObjectId,
  name: String,
  description: String,
  match_type: String (T20/ODI),
  question_ids: [ObjectId] (exactly 11),
  total_points: Number,
  is_active: Boolean,
  created_at: Date
}

// 5. contests
{
  _id: ObjectId,
  match_id: ObjectId,
  template_id: ObjectId,
  name: String,
  entry_fee: Number (virtual coins),
  prize_pool: Number,
  prize_distribution: [
    { rank_start: 1, rank_end: 1, prize: Number },
    { rank_start: 2, rank_end: 3, prize: Number },
    // ...
  ],
  max_participants: Number,
  current_participants: Number,
  status: String (open/locked/live/completed/cancelled),
  lock_time: Date,
  created_at: Date
}

// 6. contest_entries
{
  _id: ObjectId,
  contest_id: ObjectId,
  user_id: ObjectId,
  team_name: String,
  predictions: [
    {
      question_id: ObjectId,
      selected_option: String (A/B/C/D),
      is_correct: Boolean (null until resolved),
      points_earned: Number
    }
  ],
  total_points: Number,
  submission_time: Date,
  final_rank: Number,
  prize_won: Number,
  created_at: Date
}

// 7. question_results
{
  _id: ObjectId,
  match_id: ObjectId,
  question_id: ObjectId,
  correct_option: String,
  resolution_data: Object,
  resolved_at: Date
}

// 8. wallet_transactions
{
  _id: ObjectId,
  user_id: ObjectId,
  type: String (credit/debit),
  amount: Number,
  reason: String (signup_bonus/daily_reward/contest_entry/contest_win/referral),
  reference_id: ObjectId,
  balance_after: Number,
  created_at: Date
}

// 9. match_state (Redis cached, MongoDB backup)
{
  match_id: String,
  innings: Number,
  overs: Number,
  balls: Number,
  runs: Number,
  wickets: Number,
  extras: Number,
  current_batsmen: Array,
  current_bowler: Object,
  recent_balls: Array,
  run_rate: Number,
  required_rate: Number,
  last_updated: Date
}
```

#### Indexes:
- users: phone (unique), referral_code (unique)
- matches: external_match_id, status, start_time
- contests: match_id, status
- contest_entries: contest_id + user_id (compound unique)
- wallet_transactions: user_id, created_at

#### Deliverables:
- [ ] All MongoDB models created
- [ ] Indexes configured
- [ ] Sample data seeding script

---

### STAGE 3: Authentication System
**Duration:** Day 3-4
**Priority:** Critical

#### Features:
1. **Registration Flow**
   - Enter phone number
   - Create 4-digit PIN
   - Auto-generate username
   - Credit 10,000 signup bonus coins

2. **Login Flow**
   - Enter phone number
   - Enter 4-digit PIN
   - JWT token generation (7 days expiry)
   - Refresh token mechanism

3. **Security (Basic)**
   - PIN hashed with bcrypt
   - Rate limiting (5 attempts, 15 min lockout)
   - JWT with phone claim

#### API Endpoints:
```
POST /api/auth/register
  Body: { phone, pin, username (optional) }
  Response: { token, refresh_token, user }

POST /api/auth/login
  Body: { phone, pin }
  Response: { token, refresh_token, user }

POST /api/auth/refresh
  Body: { refresh_token }
  Response: { token }

GET /api/auth/me
  Headers: Authorization: Bearer {token}
  Response: { user }

PUT /api/auth/change-pin
  Body: { old_pin, new_pin }
  Response: { success }
```

#### Frontend Screens:
- Welcome/Splash Screen
- Phone Number Entry
- PIN Creation (with confirm)
- Login Screen

#### Deliverables:
- [ ] Auth API complete
- [ ] JWT middleware working
- [ ] Login/Register UI complete
- [ ] Token persistence in localStorage

---

### STAGE 4: User Profile & Wallet System
**Duration:** Day 4-5
**Priority:** High

#### Features:
1. **User Profile**
   - View/Edit username
   - Avatar selection (preset avatars)
   - Stats display (matches, wins, points)
   - Rank title with progress bar

2. **Wallet System**
   - Current balance display
   - Transaction history (paginated)
   - Daily reward claim (500 coins, streak bonus)
   - Referral code share

3. **Rank System**
   ```
   Rookie: 0 - 999 points
   Pro: 1,000 - 4,999 points
   Expert: 5,000 - 14,999 points
   Legend: 15,000 - 49,999 points
   GOAT: 50,000+ points
   ```

#### API Endpoints:
```
GET /api/user/profile
PUT /api/user/profile
  Body: { username, avatar_url }

GET /api/wallet/balance
GET /api/wallet/transactions?page=1&limit=20
POST /api/wallet/claim-daily
GET /api/user/referral-stats
POST /api/user/apply-referral
  Body: { referral_code }
```

#### Daily Reward Logic:
- Day 1: 500 coins
- Day 2: 600 coins
- Day 3: 700 coins
- Day 4: 800 coins
- Day 5: 900 coins
- Day 6: 1000 coins
- Day 7+: 1000 coins + 200 streak bonus

#### Deliverables:
- [ ] Profile API & UI
- [ ] Wallet API & UI
- [ ] Daily reward working
- [ ] Transaction history UI

---

### STAGE 5: Questions Bank & Templates (Admin)
**Duration:** Day 5-7
**Priority:** High

#### Features:
1. **Questions Bank Manager**
   - CRUD for questions
   - Hindi + English support
   - Evaluation rules builder (visual)
   - Category filtering
   - Bulk import via JSON

2. **Template Manager**
   - Create template (select 11 questions)
   - Drag-drop reordering
   - Auto-calculate total points
   - Clone existing template

3. **AI Question Generation**
   - Input: Match details, Playing XI, venue
   - GPT-5.2 generates 15-20 questions
   - Admin reviews & selects 11
   - Auto-fill evaluation rules

#### Sample Questions (Hindi):
```
1. पहली पारी में कुल रन कितने बनेंगे?
   A) 150 से कम  B) 150-170  C) 171-190  D) 190 से ज्यादा

2. क्या कोई खिलाड़ी 50+ रन बनाएगा?
   A) हाँ  B) नहीं

3. Powerplay में कितने विकेट गिरेंगे?
   A) 0-1  B) 2  C) 3  D) 4+

4. मैच में कुल छक्के कितने लगेंगे?
   A) 0-8  B) 9-14  C) 15-20  D) 21+

5. पीछा करने वाली टीम जीतेगी?
   A) हाँ  B) नहीं
```

#### API Endpoints (Admin):
```
GET /api/admin/questions
POST /api/admin/questions
PUT /api/admin/questions/{id}
DELETE /api/admin/questions/{id}
POST /api/admin/questions/generate-ai
  Body: { match_id, playing_xi, venue_stats }

GET /api/admin/templates
POST /api/admin/templates
PUT /api/admin/templates/{id}
DELETE /api/admin/templates/{id}
```

#### Deliverables:
- [ ] Questions CRUD API
- [ ] Templates CRUD API
- [ ] Admin UI for both
- [ ] GPT-5.2 integration for generation
- [ ] 50+ seeded questions
- [ ] 5 ready templates

---

### STAGE 6: Match Management System
**Duration:** Day 7-9
**Priority:** Critical

#### Features:
1. **Match CRUD (Admin)**
   - Manual match creation
   - EntitySport API sync
   - Template assignment
   - Status management

2. **Match Listing (User)**
   - Upcoming matches
   - Live matches (highlighted)
   - Completed matches
   - Filter by team/status

3. **Match Detail View**
   - Teams, venue, time
   - Live score (when live)
   - Available contests
   - Questions preview

#### Match Status Flow:
```
upcoming -> live -> completed
         -> abandoned (rain/other)
         -> cancelled
```

#### EntitySport Integration:
```python
# Sync upcoming matches
GET /v2/matches?status=scheduled&per_page=50

# Get match details
GET /v2/matches/{match_id}

# Ball-by-ball (WebSocket)
WSS /v2/matches/{match_id}/live
```

#### API Endpoints:
```
GET /api/matches?status=upcoming|live|completed
GET /api/matches/{id}
GET /api/matches/{id}/live-score
POST /api/admin/matches
PUT /api/admin/matches/{id}
POST /api/admin/matches/{id}/assign-template
POST /api/admin/matches/sync-from-api
```

#### Deliverables:
- [ ] Match CRUD API
- [ ] EntitySport sync working
- [ ] Match listing UI (Home screen)
- [ ] Match detail UI
- [ ] Template assignment working

---

### STAGE 7: Contest System
**Duration:** Day 9-11
**Priority:** Critical

#### Features:
1. **Contest Types**
   - Free Contest (0 entry, small prizes)
   - Mini Contest (100 coins entry)
   - Mega Contest (500 coins entry)
   - Grand Contest (1000 coins entry)

2. **Prize Distribution**
   ```
   Mega Contest (500 entry, 85 players):
   Prize Pool: 40,000 coins
   
   Rank 1: 10,000 coins
   Rank 2-3: 5,000 coins each
   Rank 4-10: 2,000 coins each
   Rank 11-20: 500 coins each
   ```

3. **Contest Lifecycle**
   ```
   open -> locked (15 min before match) -> live -> completed
        -> cancelled (if < min_participants or match abandoned)
   ```

4. **Join Flow**
   - Check balance >= entry_fee
   - Deduct coins
   - Create contest_entry
   - Show confirmation

#### API Endpoints:
```
GET /api/matches/{match_id}/contests
GET /api/contests/{id}
POST /api/contests/{id}/join
  Body: { team_name }
GET /api/contests/{id}/my-entry
GET /api/user/my-contests?status=active|completed

POST /api/admin/contests
PUT /api/admin/contests/{id}
POST /api/admin/contests/{id}/cancel
```

#### Deliverables:
- [ ] Contest CRUD API
- [ ] Join contest flow
- [ ] Coin deduction working
- [ ] Contest listing UI
- [ ] My Contests tab

---

### STAGE 8: Prediction Submission System
**Duration:** Day 11-13
**Priority:** Critical

#### Features:
1. **Questions Display**
   - 11 questions per contest
   - Hindi primary, English toggle
   - 4 options each (A/B/C/D)
   - Points & multiplier shown

2. **Answer Selection**
   - Tap to select option
   - Can change until lock time
   - Visual feedback (selected state)
   - Progress indicator (7/11 answered)

3. **Submission Logic**
   - All 11 must be answered
   - Lock 15 min before match
   - Store submission timestamp (for tiebreaker)
   - Cannot modify after lock

4. **UI States**
   - Unanswered: Default
   - Selected: Highlighted
   - Locked: Cannot change
   - Correct: Green tick (after resolution)
   - Wrong: Red cross (after resolution)

#### API Endpoints:
```
GET /api/contests/{id}/questions
POST /api/predictions/submit
  Body: {
    contest_id,
    answers: [
      { question_id, selected_option },
      ...
    ]
  }
GET /api/predictions/my/{contest_id}
```

#### Deliverables:
- [ ] Questions display UI
- [ ] Answer selection flow
- [ ] Submit predictions API
- [ ] Lock mechanism working
- [ ] Confirmation screen

---

### STAGE 9: Scoring Engine (HEART OF THE APP)
**Duration:** Day 13-16
**Priority:** CRITICAL

#### Architecture:
```
[EntitySport WebSocket]
        |
        v
[Ball Event Receiver]
        |
        v
[Match State Accumulator] --> [Redis Cache]
        |
        v
[Resolution Trigger Checker]
        |
        v
[Question Evaluator]
        |
        v
[Batch Score Calculator]
        |
        v
[Redis Leaderboard Update] --> [Socket.IO Broadcast]
        |
        v
[MongoDB Persistence]
```

#### Match State Accumulator:
```python
class MatchStateAccumulator:
    def process_ball(self, ball_event):
        # Update running totals
        state = {
            "innings": ball_event.innings,
            "overs": ball_event.over,
            "balls": ball_event.ball,
            "total_runs": self.total_runs + ball_event.runs,
            "total_wickets": self.total_wickets + (1 if ball_event.is_wicket else 0),
            "total_fours": self.total_fours + (1 if ball_event.runs == 4 else 0),
            "total_sixes": self.total_sixes + (1 if ball_event.is_six else 0),
            "extras": self.extras + ball_event.extras,
            "powerplay_runs": ...,
            "death_overs_runs": ...,
            # ... more metrics
        }
        # Cache in Redis
        redis.hset(f"match:{match_id}:state", mapping=state)
```

#### Resolution Triggers:
```python
TRIGGERS = {
    "powerplay_end": lambda state: state.overs == 6,
    "innings_end": lambda state: state.wickets == 10 or state.overs == 20,
    "match_end": lambda state: state.match_status == "completed",
    "specific_over": lambda state, over: state.overs == over,
}
```

#### Question Evaluator:
```python
def evaluate_question(question, match_state):
    rules = question.evaluation_rules
    
    if rules.type == "range_match":
        value = match_state[rules.metric]
        for option in question.options:
            if option.min <= value <= option.max:
                return option.key
    
    elif rules.type == "boolean_match":
        value = match_state[rules.metric]
        return "A" if rules.condition(value) else "B"
    
    elif rules.type == "compound_match":
        # Multiple conditions
        pass
    
    elif rules.type == "dual_range_match":
        # Two metrics
        pass
```

#### Batch Score Calculator:
```python
async def calculate_scores(match_id, question_id, correct_option):
    # 1. Store result
    db.question_results.insert_one({
        "match_id": match_id,
        "question_id": question_id,
        "correct_option": correct_option,
        "resolved_at": datetime.utcnow()
    })
    
    # 2. Get all predictions for this question
    entries = db.contest_entries.find({
        "predictions.question_id": question_id
    })
    
    # 3. Batch update
    bulk_ops = []
    leaderboard_updates = []
    
    for entry in entries:
        prediction = find_prediction(entry, question_id)
        is_correct = prediction.selected_option == correct_option
        points = question.points * question.multiplier if is_correct else 0
        
        bulk_ops.append(UpdateOne(
            {"_id": entry._id, "predictions.question_id": question_id},
            {"$set": {
                "predictions.$.is_correct": is_correct,
                "predictions.$.points_earned": points
            },
            "$inc": {"total_points": points}}
        ))
        
        leaderboard_updates.append((entry.contest_id, entry.user_id, points))
    
    # 4. Execute bulk update
    db.contest_entries.bulk_write(bulk_ops)
    
    # 5. Update Redis leaderboards
    pipe = redis.pipeline()
    for contest_id, user_id, points in leaderboard_updates:
        pipe.zincrby(f"leaderboard:{contest_id}", points, str(user_id))
    pipe.execute()
    
    # 6. Broadcast update
    socketio.emit(f"contest:{contest_id}:leaderboard_update")
```

#### Deliverables:
- [ ] Match state accumulator
- [ ] Redis caching for state
- [ ] Resolution trigger system
- [ ] Question evaluator (all types)
- [ ] Batch score calculator
- [ ] Full pipeline tested with mock data

---

### STAGE 10: Real-time Leaderboard System
**Duration:** Day 16-18
**Priority:** High

#### Features:
1. **Leaderboard Display**
   - Rank, Username, Team Name, Points
   - Your rank highlighted
   - Top 50 + your position
   - Real-time updates via Socket.IO

2. **User Details Modal**
   - Click on user to see their answers
   - Question-wise breakdown
   - Correct/Wrong indicators
   - Points earned per question

3. **Tie-breaking**
   ```
   Composite Score = points * 1,000,000 + (MAX_TIMESTAMP - submission_time)
   ```
   - Earlier submission wins tie

4. **Performance**
   - Redis Sorted Sets for O(log N) operations
   - Target: < 50ms query time
   - Support 5000 concurrent users

#### Redis Commands:
```
# Add/Update score
ZINCRBY leaderboard:{contest_id} {points} {user_id}

# Get rank
ZREVRANK leaderboard:{contest_id} {user_id}

# Get top 50
ZREVRANGE leaderboard:{contest_id} 0 49 WITHSCORES

# Get around user
ZREVRANGE leaderboard:{contest_id} {rank-2} {rank+2} WITHSCORES
```

#### API Endpoints:
```
GET /api/contests/{id}/leaderboard?limit=50
GET /api/contests/{id}/leaderboard/me
GET /api/contests/{id}/leaderboard/user/{user_id}
WebSocket: contest:{id}:leaderboard_update
```

#### Deliverables:
- [ ] Redis leaderboard implementation
- [ ] Leaderboard API
- [ ] Real-time Socket.IO updates
- [ ] User answers modal UI
- [ ] Performance tested

---

### STAGE 11: Live Match Integration
**Duration:** Day 18-20
**Priority:** Critical

#### Features:
1. **EntitySport WebSocket Connection**
   - Connect on match start
   - Process ball-by-ball events
   - Handle reconnection
   - Error handling

2. **Live Score Display**
   - Current score, overs, wickets
   - Run rate, required rate
   - Current batsmen stats
   - Recent balls (last 6)

3. **Real-time Updates**
   - Score updates
   - Wicket alerts
   - Question resolution notifications
   - Leaderboard changes

#### WebSocket Event Flow:
```python
# Backend WebSocket handler
@websocket.on("ball_event")
async def handle_ball(data):
    match_id = data["match_id"]
    
    # 1. Update match state
    accumulator.process_ball(data)
    
    # 2. Check triggers
    resolved_questions = trigger_checker.check(match_id)
    
    # 3. Evaluate & score
    for question in resolved_questions:
        correct = evaluator.evaluate(question, match_state)
        await scorer.calculate_scores(match_id, question.id, correct)
    
    # 4. Broadcast to clients
    socketio.emit(f"match:{match_id}:score_update", match_state)
```

#### Fallback (Polling):
```python
# If WebSocket fails, poll every 10 seconds
async def poll_live_score(match_id):
    while match.status == "live":
        data = await entitysport.get_live_score(match_id)
        process_update(data)
        await asyncio.sleep(10)
```

#### Deliverables:
- [ ] EntitySport WebSocket integration
- [ ] Ball event processing
- [ ] Live score UI component
- [ ] Real-time score updates
- [ ] Fallback polling mechanism

---

### STAGE 12: Result Declaration & Prize Distribution
**Duration:** Day 20-22
**Priority:** High

#### Features:
1. **Auto Result Declaration**
   - Triggered when match ends
   - All questions resolved
   - Final leaderboard frozen
   - Prizes calculated

2. **Prize Distribution**
   ```python
   def distribute_prizes(contest_id):
       leaderboard = get_final_leaderboard(contest_id)
       contest = get_contest(contest_id)
       
       for rank, entry in enumerate(leaderboard, 1):
           prize = calculate_prize(rank, contest.prize_distribution)
           if prize > 0:
               credit_wallet(entry.user_id, prize, "contest_win", contest_id)
               update_entry_prize(entry.id, rank, prize)
       
       contest.status = "completed"
       contest.save()
   ```

3. **User Notifications**
   - Push notification for results
   - In-app notification
   - Prize credited message

4. **Results UI**
   - Final leaderboard
   - Your final rank & prize
   - Question-wise results
   - Points breakdown

#### Edge Cases:
- **Match Abandoned:** Cancel contest, refund entry fees
- **Insufficient Participants:** Cancel if < min, refund
- **Tie at Winning Position:** Earlier submission wins

#### API Endpoints:
```
POST /api/admin/contests/{id}/declare-results
GET /api/contests/{id}/results
GET /api/contests/{id}/my-results
```

#### Deliverables:
- [ ] Auto result declaration
- [ ] Prize distribution logic
- [ ] Refund logic for cancelled
- [ ] Results UI screen
- [ ] Notifications

---

### STAGE 13: Home Screen & Navigation
**Duration:** Day 22-24
**Priority:** High

#### Home Screen Layout:
```
+----------------------------------+
|  [Profile Icon]    CrickPredict  |
+----------------------------------+
|  "Revolution in Fantasy Cricket" |
+----------------------------------+
| My Balance          | + Deposit  |
| 33,500 coins        | (disabled) |
+----------------------------------+
|  Live Matches                    |
| [DC vs RCB] [MI vs LSG] [KKR...] |
|    LIVE       LIVE      LIVE     |
+----------------------------------+
|  Hot Contests                    |
| MI vs LSG - 1000 prize  [JOIN]   |
| DC vs RCB - 5000 prize  [JOIN]   |
+----------------------------------+
|  Upcoming Matches                |
| Tomorrow 7:30 PM - CSK vs GT     |
+----------------------------------+

[Home] [My Contest] [*] [Wallet] [Legal]
```

#### Bottom Navigation:
1. **Home** - Live matches, contests
2. **My Contest** - Active & past entries
3. **Center Button** - Quick join popular contest
4. **Wallet** - Balance, transactions
5. **Legal** - Terms, Privacy, Fair Play

#### Features:
- Pull to refresh
- Skeleton loading
- Match countdown timer
- Hot contest badges

#### Deliverables:
- [ ] Home screen complete
- [ ] Bottom navigation
- [ ] All tabs functional
- [ ] Smooth animations
- [ ] Pull to refresh

---

### STAGE 14: Admin Panel
**Duration:** Day 24-26
**Priority:** Medium

#### Admin Features:
1. **Dashboard**
   - Total users, active users
   - Ongoing contests
   - Revenue metrics (coins flow)
   - Recent activities

2. **Match Management**
   - Sync from EntitySport
   - Manual create/edit
   - Template assignment
   - Live monitor

3. **Contest Management**
   - Create contests for matches
   - Edit prize pools
   - Cancel/refund
   - Declare results manually

4. **User Management**
   - Search users
   - View profile & history
   - Credit/Debit coins
   - Ban/Unban

5. **Questions & Templates**
   - Already covered in Stage 5

#### Admin Authentication:
- Separate admin login
- Role-based access
- Audit logs

#### Deliverables:
- [ ] Admin dashboard
- [ ] All CRUD interfaces
- [ ] User management
- [ ] Live match monitor

---

### STAGE 15: Polish, Testing & Deployment
**Duration:** Day 26-30
**Priority:** Critical

#### Polish:
1. **UI/UX Refinements**
   - Micro-animations
   - Loading states
   - Error states
   - Empty states
   - Success feedback

2. **Performance**
   - API response < 200ms
   - Leaderboard < 50ms
   - App load < 3 seconds
   - Image optimization

3. **PWA Enhancements**
   - Offline support (cached data)
   - Push notifications
   - Install prompt
   - Splash screen

#### Testing:
1. **Unit Tests**
   - Scoring engine (critical)
   - Wallet operations
   - Auth flow

2. **Integration Tests**
   - Full contest flow
   - Payment flow
   - Leaderboard updates

3. **E2E Tests**
   - User registration to prize win
   - Admin flow

4. **Load Testing**
   - 5000 concurrent users
   - WebSocket connections
   - Leaderboard queries

#### Security:
- Rate limiting
- Input validation
- XSS prevention
- CORS configuration
- PIN attempt limiting

#### Deployment:
- Docker containers
- MongoDB Atlas
- Redis Cloud
- AWS/Vercel hosting
- SSL certificates
- Domain setup

#### Deliverables:
- [ ] All tests passing
- [ ] Performance benchmarks met
- [ ] Security audit complete
- [ ] Production deployment
- [ ] PWA published

---

## DEVELOPMENT TIMELINE SUMMARY

| Stage | Name | Days | Priority |
|-------|------|------|----------|
| 1 | Project Foundation | 1-2 | Critical |
| 2 | Database Schema | 2-3 | Critical |
| 3 | Authentication | 3-4 | Critical |
| 4 | User Profile & Wallet | 4-5 | High |
| 5 | Questions & Templates | 5-7 | High |
| 6 | Match Management | 7-9 | Critical |
| 7 | Contest System | 9-11 | Critical |
| 8 | Prediction Submission | 11-13 | Critical |
| 9 | Scoring Engine | 13-16 | CRITICAL |
| 10 | Leaderboard System | 16-18 | High |
| 11 | Live Match Integration | 18-20 | Critical |
| 12 | Result & Prize Distribution | 20-22 | High |
| 13 | Home & Navigation | 22-24 | High |
| 14 | Admin Panel | 24-26 | Medium |
| 15 | Polish & Deployment | 26-30 | Critical |

**Total Estimated Duration: 30 Days**

---

## TECH STACK FINAL

### Frontend
- React.js 18+
- Tailwind CSS
- Socket.IO Client
- PWA (Service Worker)
- Zustand (State Management)

### Backend
- Python FastAPI
- Motor (Async MongoDB)
- Redis (aioredis)
- Socket.IO (python-socketio)
- Pydantic (Validation)

### Database
- MongoDB Atlas
- Redis Cloud

### External APIs
- EntitySport (Cricket Data)
- GPT-5.2 via Emergent LLM Key (AI Questions)

### Hosting
- Vercel (Frontend PWA)
- AWS/Railway (Backend)
- MongoDB Atlas (Database)
- Redis Cloud (Cache)

---

## CRICKET API PURCHASE INFO

### EntitySport
- **Website:** https://entitysport.com
- **Plan:** Cricket Starter ($150/month)
- **Includes:**
  - 500K API calls/month
  - Ball-by-ball data
  - Live scores
  - Player images
- **For Real-time:** Push API (Custom pricing, contact sales)

### Alternative: Roanuz
- **Website:** https://cricketapi.com
- **IPL Plan:** ₹24,999/month (~$300)
- **Includes:**
  - Native WebSocket
  - Ball-by-ball "as fast as TV"
  - Webhook support

---

## NEXT STEPS

1. **Purchase EntitySport API** - Get API key
2. **Setup Development Environment** - Emergent platform
3. **Start Stage 1** - Foundation setup
4. **Parallel Development** - Backend + Frontend together

Ready to start building when you give the go-ahead!
