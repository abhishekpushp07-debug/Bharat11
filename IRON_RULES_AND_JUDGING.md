# CrickPredict - 5 IRON RULES & 50-POINT JUDGING FRAMEWORK

---

## 🔒 5 IRON RULES (NEVER BREAK)

```
╔═══════════════════════════════════════════════════════════════════╗
║  RULE 1: World's Best Code - Stage by Stage                      ║
║  RULE 2: Honestly Judge on 50 Points after Stage Completion      ║
║  RULE 3: Optimize until ALL Points reach 90+ (out of 100)        ║
║  RULE 4: Re-Judge on 50 Points (Redis, Canonical, Optimizations) ║
║  RULE 5: Only Then Move to Next Stage - Repeat Rules 1-5         ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## 📊 50-POINT JUDGING FRAMEWORK (Per Stage)

### CATEGORY A: CODE QUALITY (15 Points)

| # | Criteria | Max Points | 90+ Target |
|---|----------|------------|------------|
| 1 | Clean Architecture (Separation of Concerns) | 3 | ≥2.7 |
| 2 | SOLID Principles Applied | 3 | ≥2.7 |
| 3 | DRY - No Code Duplication | 3 | ≥2.7 |
| 4 | Proper Error Handling & Edge Cases | 3 | ≥2.7 |
| 5 | Code Readability & Documentation | 3 | ≥2.7 |

### CATEGORY B: PERFORMANCE (15 Points)

| # | Criteria | Max Points | 90+ Target |
|---|----------|------------|------------|
| 6 | Redis Usage (Caching, Sorted Sets, Pub/Sub) | 3 | ≥2.7 |
| 7 | Database Queries Optimized (Indexes, Projections) | 3 | ≥2.7 |
| 8 | API Response Time (<200ms) | 3 | ≥2.7 |
| 9 | Memory Efficient (No Leaks, Proper Cleanup) | 3 | ≥2.7 |
| 10 | Async/Concurrent Operations Used | 3 | ≥2.7 |

### CATEGORY C: DATA INTEGRITY (10 Points)

| # | Criteria | Max Points | 90+ Target |
|---|----------|------------|------------|
| 11 | Canonical Data Models (Single Source of Truth) | 2.5 | ≥2.25 |
| 12 | Data Validation (Pydantic Strict Mode) | 2.5 | ≥2.25 |
| 13 | Atomic Transactions (No Partial Updates) | 2.5 | ≥2.25 |
| 14 | Idempotent Operations | 2.5 | ≥2.25 |

### CATEGORY D: SCALABILITY (5 Points)

| # | Criteria | Max Points | 90+ Target |
|---|----------|------------|------------|
| 15 | Horizontal Scalability Ready | 2.5 | ≥2.25 |
| 16 | Connection Pooling & Resource Management | 2.5 | ≥2.25 |

### CATEGORY E: SECURITY (5 Points)

| # | Criteria | Max Points | 90+ Target |
|---|----------|------------|------------|
| 17 | Input Sanitization & Validation | 2.5 | ≥2.25 |
| 18 | Rate Limiting & Abuse Prevention | 2.5 | ≥2.25 |

---

## 📋 STAGE EVALUATION TEMPLATE

```markdown
## STAGE [X] EVALUATION - [Stage Name]

### First Evaluation (After Completion)
| Category | Points | Score | % |
|----------|--------|-------|---|
| A. Code Quality | /15 | | |
| B. Performance | /15 | | |
| C. Data Integrity | /10 | | |
| D. Scalability | /5 | | |
| E. Security | /5 | | |
| **TOTAL** | **/50** | | |

### Issues Found:
1. [Issue 1] - Category X - Current Score: Y
2. [Issue 2] - Category X - Current Score: Y

### Optimization Plan:
- [ ] Fix Issue 1: [Solution]
- [ ] Fix Issue 2: [Solution]

---

### Second Evaluation (After Optimization)
| Category | Points | Score | % |
|----------|--------|-------|---|
| A. Code Quality | /15 | | |
| B. Performance | /15 | | |
| C. Data Integrity | /10 | | |
| D. Scalability | /5 | | |
| E. Security | /5 | | |
| **TOTAL** | **/50** | | |

### ✅ All criteria at 90%+ : [YES/NO]
### ➡️ Ready for Next Stage: [YES/NO]
```

---

## 🏏 FREE CRICKET SCORE SOLUTION (Google/Cricbuzz Scraping)

### Original Plan: EntitySport API ($150/month)
### New Plan: FREE Cricbuzz Scraping (2-ball delay acceptable)

### Solution: sanwebinfo/cricket-api

**Repository:** https://github.com/sanwebinfo/cricket-api

**How it works:**
1. Scrapes Cricbuzz live score pages
2. Returns JSON with ball-by-ball data
3. Self-hosted = Unlimited requests
4. 2-3 second delay (acceptable for our use case)

### Data Available (FREE):
```json
{
  "title": "MI vs CSK, IPL 2026 - Live",
  "livescore": "MI 168/3 (16.2)",
  "runrate": "CRR: 10.28",
  "batterone": "Rohit Sharma",
  "batsmanonerun": "72",
  "batsmanoneball": "(48)",
  "batsmanonesr": "150.00",
  "battertwo": "Suryakumar Yadav",
  "batsmantworun": "45",
  "batsmantwoball": "(28)",
  "batsmantwosr": "160.71",
  "bowlerone": "Deepak Chahar",
  "bowleroneover": "3.2",
  "bowleronerun": "28",
  "bowleronewickers": "1",
  "bowleroneeconomy": "8.40"
}
```

### Integration Plan:
```python
# Our custom scraper (enhanced version)
class CricbuzzScraper:
    BASE_URL = "https://www.cricbuzz.com/live-cricket-scores"
    
    async def get_live_score(self, match_id: str) -> MatchScore:
        """Scrape live score with 2-3 second delay"""
        # Scraping logic
        pass
    
    async def get_ball_by_ball(self, match_id: str) -> List[BallEvent]:
        """Get recent balls for scoring engine"""
        # Parse commentary for ball events
        pass
    
    async def get_match_list(self) -> List[LiveMatch]:
        """Get all live matches"""
        pass
```

### Advantages:
- ✅ 100% FREE
- ✅ Reliable (Cricbuzz is stable)
- ✅ Sufficient data for scoring engine
- ✅ 2-ball delay is acceptable (not betting app)

### Limitations:
- ⚠️ 2-3 second delay (acceptable)
- ⚠️ May break if Cricbuzz changes HTML (we'll monitor)
- ⚠️ Need to extract match IDs manually (or scrape list)

---

## 📅 UPDATED STAGE FLOW

```
┌──────────────────────────────────────────────────────────────┐
│                     STAGE EXECUTION FLOW                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────┐                                            │
│   │  STAGE N    │                                            │
│   │  Development│                                            │
│   └──────┬──────┘                                            │
│          │                                                   │
│          ▼                                                   │
│   ┌─────────────┐                                            │
│   │ 1st Judge   │──── Score < 90%? ──── YES ───┐            │
│   │ (50 Points) │                              │            │
│   └──────┬──────┘                              │            │
│          │ NO                                  │            │
│          ▼                                     ▼            │
│   ┌─────────────┐                    ┌─────────────┐        │
│   │ All 90%+?   │                    │  Optimize   │        │
│   │             │                    │  - Redis    │        │
│   └──────┬──────┘                    │  - Canonical│        │
│          │ YES                       │  - Perf     │        │
│          ▼                           └──────┬──────┘        │
│   ┌─────────────┐                           │              │
│   │ 2nd Judge   │◄──────────────────────────┘              │
│   │ (50 Points) │                                          │
│   └──────┬──────┘                                          │
│          │                                                  │
│          ▼                                                  │
│   ┌─────────────┐                                          │
│   │ All 90%+?   │──── NO ──── Back to Optimize             │
│   └──────┬──────┘                                          │
│          │ YES                                             │
│          ▼                                                  │
│   ┌─────────────┐                                          │
│   │ STAGE N+1   │                                          │
│   │ (Next)      │                                          │
│   └─────────────┘                                          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎯 OPTIMIZATION CHECKLIST (For 90%+ Score)

### Redis Best Practices:
- [ ] Use Redis Sorted Sets for leaderboards (ZADD, ZINCRBY, ZREVRANK)
- [ ] Cache hot data with TTL (match state, user sessions)
- [ ] Use Redis Pub/Sub for real-time events
- [ ] Pipeline multiple commands (reduce round trips)
- [ ] Use Redis Streams for event sourcing

### MongoDB Best Practices:
- [ ] Proper indexes on all query fields
- [ ] Use projections (only fetch needed fields)
- [ ] Compound indexes for common queries
- [ ] Use aggregation pipelines efficiently
- [ ] Avoid $where and regex on large collections

### Canonical Data Patterns:
- [ ] Single source of truth for each entity
- [ ] Use references (ObjectId) not embedded duplicates
- [ ] Denormalize only for read performance (with sync)
- [ ] Use enums for status fields
- [ ] Timestamps in UTC (ISO format)

### Code Architecture:
- [ ] Repository pattern for data access
- [ ] Service layer for business logic
- [ ] DTOs for API input/output
- [ ] Dependency injection
- [ ] Factory pattern for complex objects

### Performance Optimizations:
- [ ] Connection pooling (MongoDB, Redis)
- [ ] Async/await everywhere (no blocking)
- [ ] Batch operations (bulk_write, pipeline)
- [ ] Lazy loading where appropriate
- [ ] Response compression (gzip)

---

## ✅ READY TO START

Stage 1 शुरू करने के लिए confirm करें!

मैं हर stage के बाद:
1. Code complete करूंगा
2. 50-point पर honestly judge करूंगा
3. 90%+ तक optimize करूंगा
4. Re-judge करूंगा
5. तभी next stage पर जाऊंगा
