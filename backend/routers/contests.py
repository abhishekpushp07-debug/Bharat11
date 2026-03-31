"""
Contest Router
Handles contest management, joining, predictions, and scoring.
The HEART of the application.
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta

from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import get_db, db_manager
from core.dependencies import CurrentUser
from core.exceptions import CrickPredictException, InsufficientBalanceError
from core.redis_manager import RedisManager
from models.schemas import (
    ContestStatus, TransactionType, TransactionReason,
    generate_id, utc_now
)


router = APIRouter(prefix="/contests", tags=["Contests"])


# ==================== DTOs ====================

class PrizeDistItem(BaseModel):
    rank_start: int = Field(..., ge=1)
    rank_end: int = Field(..., ge=1)
    prize: int = Field(..., ge=0)


class ContestCreate(BaseModel):
    match_id: str
    template_id: str
    name: str
    entry_fee: int = Field(default=0, ge=0)
    prize_pool: int = Field(default=0, ge=0)
    max_participants: int = Field(default=100, ge=2)
    prize_distribution: list[PrizeDistItem] = Field(default_factory=list)
    lock_time: str  # ISO format


class JoinContest(BaseModel):
    team_name: str = Field(..., min_length=1, max_length=50)


class PredictionItem(BaseModel):
    question_id: str
    selected_option: str = Field(..., pattern="^[A-D]$")


class SubmitPredictions(BaseModel):
    predictions: list[PredictionItem] = Field(..., min_length=1, max_length=50)


class ResolveQuestion(BaseModel):
    question_id: str
    correct_option: str = Field(..., pattern="^[A-D]$")


# ==================== CONTEST CRUD ====================

@router.get(
    "",
    summary="List contests",
    description="List contests with optional status filter"
)
async def list_contests(
    db: AsyncIOMotorDatabase = Depends(get_db),
    contest_status: Optional[str] = Query(default=None, alias="status"),
    match_id: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=50)
):
    query = {}
    if contest_status:
        query["status"] = contest_status
    if match_id:
        query["match_id"] = match_id

    skip = (page - 1) * limit
    cursor = db.contests.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
    contests = await cursor.to_list(length=limit)
    total = await db.contests.count_documents(query)

    return {"contests": contests, "page": page, "limit": limit, "total": total, "has_more": (page * limit) < total}


@router.get(
    "/{contest_id}",
    summary="Get contest details"
)
async def get_contest(
    contest_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    contest = await db.contests.find_one({"id": contest_id}, {"_id": 0})
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")

    # Get match info
    match = await db.matches.find_one(
        {"id": contest.get("match_id")},
        {"_id": 0, "team_a": 1, "team_b": 1, "venue": 1, "status": 1, "start_time": 1, "tournament": 1}
    )
    contest["match"] = match
    return contest


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create contest (Admin)"
)
async def create_contest(
    data: ContestCreate,
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    # Verify match exists
    match = await db.matches.find_one({"id": data.match_id}, {"_id": 0, "id": 1})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Verify template exists
    template = await db.templates.find_one({"id": data.template_id}, {"_id": 0, "id": 1})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    now = utc_now().isoformat()
    contest = {
        "id": generate_id(),
        "match_id": data.match_id,
        "template_id": data.template_id,
        "name": data.name,
        "entry_fee": data.entry_fee,
        "prize_pool": data.prize_pool,
        "prize_distribution": [p.model_dump() for p in data.prize_distribution],
        "max_participants": data.max_participants,
        "current_participants": 0,
        "status": "open",
        "lock_time": data.lock_time,
        "created_at": now,
        "updated_at": now
    }
    await db.contests.insert_one(contest)
    del contest["_id"]
    return contest


# ==================== JOIN CONTEST ====================

@router.post(
    "/{contest_id}/join",
    summary="Join a contest",
    description="Join contest: check balance, deduct entry fee, create entry"
)
async def join_contest(
    contest_id: str,
    data: JoinContest,
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    # 1. Get contest
    contest = await db.contests.find_one({"id": contest_id})
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")

    if contest["status"] not in ("open", "live"):
        raise HTTPException(status_code=400, detail="Contest is not open for joining")

    # Check lock time
    lock_time = contest.get("lock_time", "")
    if lock_time:
        lt = datetime.fromisoformat(lock_time.replace('Z', '+00:00')) if isinstance(lock_time, str) else lock_time
        # Ensure timezone-aware comparison
        if lt.tzinfo is None:
            lt = lt.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) >= lt:
            raise HTTPException(status_code=400, detail="Contest is locked. Cannot join after lock time")

    # Check max participants
    if contest["current_participants"] >= contest["max_participants"]:
        raise HTTPException(status_code=400, detail="Contest is full")

    # 2. Check if already joined
    existing = await db.contest_entries.find_one(
        {"contest_id": contest_id, "user_id": current_user.id}
    )
    if existing:
        raise HTTPException(status_code=409, detail="Already joined this contest")

    # 3. Get user and check balance
    user = await db.users.find_one({"id": current_user.id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    entry_fee = contest["entry_fee"]
    if entry_fee > 0 and user["coins_balance"] < entry_fee:
        raise HTTPException(status_code=400, detail=f"Insufficient balance. Need {entry_fee} coins, have {user['coins_balance']}")

    now = utc_now().isoformat()

    # 4. Deduct entry fee (atomic with $gte guard)
    if entry_fee > 0:
        debit_result = await db.users.update_one(
            {"id": current_user.id, "coins_balance": {"$gte": entry_fee}},
            {"$inc": {"coins_balance": -entry_fee}, "$set": {"updated_at": now}}
        )
        if debit_result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Insufficient balance (race condition guard)")
        
        new_balance = user["coins_balance"] - entry_fee
        # Create transaction
        await db.wallet_transactions.insert_one({
            "id": generate_id(),
            "user_id": current_user.id,
            "type": "debit",
            "amount": entry_fee,
            "reason": "contest_entry",
            "reference_id": contest_id,
            "balance_after": new_balance,
            "description": f"Entry fee for {contest['name']}",
            "created_at": now,
            "updated_at": now
        })
    else:
        new_balance = user["coins_balance"]

    # 5. Create contest entry
    entry = {
        "id": generate_id(),
        "contest_id": contest_id,
        "user_id": current_user.id,
        "team_name": data.team_name,
        "predictions": [],
        "total_points": 0,
        "submission_time": None,
        "final_rank": None,
        "prize_won": 0,
        "created_at": now,
        "updated_at": now
    }
    try:
        await db.contest_entries.insert_one(entry)
    except Exception:
        # Rollback: refund if entry creation fails
        if entry_fee > 0:
            await db.users.update_one(
                {"id": current_user.id},
                {"$inc": {"coins_balance": entry_fee}}
            )
        raise HTTPException(status_code=500, detail="Failed to create entry. Fee refunded.")

    # 6. Increment participant count and update prize pool dynamically
    await db.contests.update_one(
        {"id": contest_id},
        {
            "$inc": {"current_participants": 1, "prize_pool": entry_fee},
            "$set": {"updated_at": now}
        }
    )

    del entry["_id"]

    # Invalidate contest caches
    from services.redis_cache import cache_invalidate_contest
    await cache_invalidate_contest(contest_id)

    return {
        "entry": entry,
        "new_balance": new_balance,
        "contest_name": contest["name"],
        "message": f"Joined {contest['name']}! {'Entry fee: ' + str(entry_fee) + ' coins deducted.' if entry_fee > 0 else 'Free entry!'}"
    }


# ==================== PREDICTIONS ====================

@router.get(
    "/{contest_id}/questions",
    summary="Get contest questions",
    description="Get the 11 questions for this contest (from assigned template)"
)
async def get_contest_questions(
    contest_id: str,
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    contest = await db.contests.find_one({"id": contest_id}, {"_id": 0})
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")

    # Cache questions (they rarely change) — but NOT user predictions or lock status
    from services.redis_cache import cache_get, cache_set, CacheTTL
    q_cache_key = f"contest:{contest_id}:questions"
    cached_q = await cache_get(q_cache_key)

    if cached_q:
        ordered = cached_q["questions"]
        template_name = cached_q["template_name"]
    else:
        # Get template
        template = await db.templates.find_one({"id": contest.get("template_id")}, {"_id": 0})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        # Get questions
        qids = template.get("question_ids", [])
        cursor = db.questions.find({"id": {"$in": qids}}, {"_id": 0})
        questions = await cursor.to_list(length=len(qids))

        # Maintain order
        q_map = {q["id"]: q for q in questions}
        ordered = [q_map[qid] for qid in qids if qid in q_map]
        template_name = template.get("name", "")
        await cache_set(q_cache_key, {"questions": ordered, "template_name": template_name}, 600)

    # Check if user has existing predictions
    entry = await db.contest_entries.find_one(
        {"contest_id": contest_id, "user_id": current_user.id},
        {"_id": 0, "predictions": 1, "submission_time": 1}
    )

    # Check lock status
    lock_time = contest.get("lock_time", "")
    is_locked = False
    if lock_time:
        lt = datetime.fromisoformat(lock_time.replace('Z', '+00:00')) if isinstance(lock_time, str) else lock_time
        if lt.tzinfo is None:
            lt = lt.replace(tzinfo=timezone.utc)
        is_locked = datetime.now(timezone.utc) >= lt

    return {
        "contest_id": contest_id,
        "template_name": template_name,
        "questions": ordered,
        "total_questions": len(ordered),
        "total_points": sum(q.get("points", 10) for q in ordered),
        "is_locked": is_locked,
        "lock_time": lock_time,
        "my_predictions": entry.get("predictions", []) if entry else [],
        "submitted_at": entry.get("submission_time") if entry else None
    }


@router.post(
    "/{contest_id}/predict",
    summary="Submit predictions",
    description="Submit answers for all contest questions. Can update until lock time."
)
async def submit_predictions(
    contest_id: str,
    data: SubmitPredictions,
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    # 1. Verify contest
    contest = await db.contests.find_one({"id": contest_id})
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")

    # 2. Check lock time (basic time check)
    lock_time = contest.get("lock_time", "")
    if lock_time:
        lt = datetime.fromisoformat(lock_time.replace('Z', '+00:00')) if isinstance(lock_time, str) else lock_time
        if lt.tzinfo is None:
            lt = lt.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) >= lt:
            raise HTTPException(status_code=400, detail="Contest is locked. Predictions cannot be modified")

    # 2b. Check template deadline (over-based enforcement — HARD RULE)
    template = await db.templates.find_one({"id": contest.get("template_id")}, {"_id": 0})
    if template:
        from services.match_engine import check_can_submit
        match_id = contest.get("match_id", "")
        deadline_check = await check_can_submit(template, match_id, db)
        if not deadline_check["can_submit"]:
            raise HTTPException(
                status_code=400,
                detail=f"Template locked! {deadline_check['reason']}"
            )

    # 3. Verify user has joined
    entry = await db.contest_entries.find_one(
        {"contest_id": contest_id, "user_id": current_user.id}
    )
    if not entry:
        raise HTTPException(status_code=403, detail="You haven't joined this contest. Join first.")

    # 4. Validate question IDs belong to contest template
    if not template:
        template = await db.templates.find_one({"id": contest.get("template_id")}, {"_id": 0})
    valid_qids = set(template.get("question_ids", [])) if template else set()

    predictions = []
    for p in data.predictions:
        if p.question_id not in valid_qids:
            raise HTTPException(status_code=400, detail=f"Question {p.question_id} is not part of this contest")
        predictions.append({
            "question_id": p.question_id,
            "selected_option": p.selected_option,
            "is_correct": None,
            "points_earned": 0
        })

    # 5. Update entry with predictions
    now = utc_now()
    await db.contest_entries.update_one(
        {"id": entry["id"]},
        {"$set": {
            "predictions": predictions,
            "submission_time": now.isoformat(),
            "updated_at": now.isoformat()
        }}
    )

    return {
        "entry_id": entry["id"],
        "predictions_count": len(predictions),
        "submitted_at": now.isoformat(),
        "message": f"Predictions saved! {len(predictions)} answers submitted."
    }


@router.get(
    "/{contest_id}/my-entry",
    summary="Get my contest entry",
    description="Get current user's entry and predictions for a contest"
)
async def get_my_entry(
    contest_id: str,
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    entry = await db.contest_entries.find_one(
        {"contest_id": contest_id, "user_id": current_user.id},
        {"_id": 0}
    )
    if not entry:
        raise HTTPException(status_code=404, detail="No entry found for this contest")
    return entry


# ==================== MY CONTESTS ====================

@router.get(
    "/user/my-contests",
    summary="My contests",
    description="Get all contests the current user has joined"
)
async def my_contests(
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db),
    contest_status: Optional[str] = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=50)
):
    # Get user's contest entries
    skip = (page - 1) * limit
    entry_cursor = db.contest_entries.find(
        {"user_id": current_user.id},
        {"_id": 0}
    ).sort("created_at", -1)
    all_entries = await entry_cursor.to_list(length=200)  # max 200 entries

    # Batch fetch contests + matches (avoid N+1)
    contest_ids = list(set(e["contest_id"] for e in all_entries))
    contests_cursor = db.contests.find(
        {"id": {"$in": contest_ids}},
        {"_id": 0, "id": 1, "name": 1, "status": 1, "match_id": 1, "entry_fee": 1, "prize_pool": 1, "current_participants": 1, "question_count": 1, "template_id": 1, "template_name": 1, "template_type": 1}
    )
    contests_list = await contests_cursor.to_list(length=len(contest_ids))
    contest_map = {c["id"]: c for c in contests_list}

    match_ids = list(set(c.get("match_id", "") for c in contests_list if c.get("match_id")))
    matches_cursor = db.matches.find(
        {"id": {"$in": match_ids}},
        {"_id": 0, "id": 1, "team_a": 1, "team_b": 1, "status": 1, "start_time": 1, "venue": 1, "live_score": 1}
    )
    matches_list = await matches_cursor.to_list(length=len(match_ids))

    # Add IST formatted time to each match
    from datetime import timedelta, timezone as tz
    IST_OFFSET = timedelta(hours=5, minutes=30)
    for m in matches_list:
        st = m.get("start_time", "")
        if st:
            try:
                from dateutil.parser import parse as dt_parse
                dt_obj = dt_parse(str(st)) if isinstance(st, str) else st
                if dt_obj.tzinfo is None:
                    dt_obj = dt_obj.replace(tzinfo=tz.utc)
                ist_dt = dt_obj + IST_OFFSET
                m["start_time_ist"] = ist_dt.strftime("%d %b %Y, %I:%M %p") + " IST"
            except Exception:
                m["start_time_ist"] = str(st)
    match_map = {m["id"]: m for m in matches_list}

    # Build result with filter BEFORE pagination
    result = []
    for entry in all_entries:
        contest = contest_map.get(entry["contest_id"])
        if not contest:
            continue

        if contest_status and contest.get("status") != contest_status:
            continue

        match = match_map.get(contest.get("match_id", ""))

        result.append({
            "entry": entry,
            "contest": contest,
            "match": match
        })

    # Apply pagination AFTER filtering
    total_filtered = len(result)
    paginated = result[skip:skip + limit]

    return {"my_contests": paginated, "total": total_filtered, "page": page, "has_more": (page * limit) < total_filtered}


# ==================== SCORING ENGINE (Stage 9) ====================

@router.post(
    "/{contest_id}/resolve",
    summary="Resolve a question (Admin/Scoring Engine)",
    description="Set correct answer for a question and batch-update all entries"
)
async def resolve_question(
    contest_id: str,
    data: ResolveQuestion,
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    # 1. Verify contest
    contest = await db.contests.find_one({"id": contest_id})
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")

    # 2. Check idempotency - don't re-resolve
    existing_result = await db.question_results.find_one({
        "match_id": contest["match_id"],
        "question_id": data.question_id
    })
    if existing_result:
        return {"message": "Question already resolved", "correct_option": existing_result.get("correct_option")}

    # 3. Get question for points info
    question = await db.questions.find_one({"id": data.question_id}, {"_id": 0})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    points_value = question.get("points", 10)
    now = utc_now().isoformat()

    # 4. Store question result (idempotent)
    await db.question_results.insert_one({
        "id": generate_id(),
        "match_id": contest["match_id"],
        "question_id": data.question_id,
        "correct_option": data.correct_option,
        "resolved_at": now,
        "created_at": now,
        "updated_at": now
    })

    # 5. Update question's correct_option
    await db.questions.update_one(
        {"id": data.question_id},
        {"$set": {"correct_option": data.correct_option}}
    )

    # 6. Batch score all entries for this contest
    from pymongo import UpdateOne
    entries_cursor = db.contest_entries.find(
        {"contest_id": contest_id, "predictions.question_id": data.question_id}
    )
    entries = await entries_cursor.to_list(length=10000)

    bulk_ops = []
    score_updates = []  # (user_id, points_earned)
    correct_count = 0
    wrong_count = 0
    user_correct_map = {}
    user_points_map = {}

    for entry in entries:
        for i, pred in enumerate(entry.get("predictions", [])):
            if pred["question_id"] == data.question_id:
                is_correct = pred["selected_option"] == data.correct_option
                earned = points_value if is_correct else 0

                if is_correct:
                    correct_count += 1
                    user_correct_map[entry["user_id"]] = True
                    user_points_map[entry["user_id"]] = points_value
                else:
                    wrong_count += 1
                    user_correct_map[entry["user_id"]] = False

                bulk_ops.append(UpdateOne(
                    {"_id": entry["_id"], f"predictions.{i}.question_id": data.question_id},
                    {"$set": {
                        f"predictions.{i}.is_correct": is_correct,
                        f"predictions.{i}.points_earned": earned
                    },
                    "$inc": {"total_points": earned}}
                ))
                score_updates.append((entry["user_id"], earned))
                break

    if bulk_ops:
        await db.contest_entries.bulk_write(bulk_ops)

    # 6b. Update prediction streaks and apply bonus multiplier
    from services.settlement_engine import update_user_streaks
    streak_results = await update_user_streaks(db, user_correct_map, user_points_map)

    # Apply streak bonuses to entries
    bonus_ops = []
    total_bonus = 0
    for entry in entries:
        uid = entry["user_id"]
        sr = streak_results.get(uid)
        if sr and sr["bonus"] > 0:
            total_bonus += sr["bonus"]
            for i, pred in enumerate(entry.get("predictions", [])):
                if pred["question_id"] == data.question_id:
                    bonus_ops.append(UpdateOne(
                        {"_id": entry["_id"], f"predictions.{i}.question_id": data.question_id},
                        {
                            "$inc": {
                                f"predictions.{i}.points_earned": sr["bonus"],
                                "total_points": sr["bonus"]
                            },
                            "$set": {
                                f"predictions.{i}.streak_multiplier": sr["multiplier"]
                            }
                        }
                    ))
                    break

    if bonus_ops:
        await db.contest_entries.bulk_write(bonus_ops)

    # 7. Update Redis leaderboard
    redis_mgr = RedisManager(db_manager._redis_client)
    if redis_mgr.is_available:
        for user_id, points in score_updates:
            if points > 0:
                await redis_mgr.leaderboard_upsert(
                    contest_id, user_id, points
                )

    return {
        "question_id": data.question_id,
        "correct_option": data.correct_option,
        "entries_evaluated": len(entries),
        "correct": correct_count,
        "wrong": wrong_count,
        "points_value": points_value,
        "streak_bonuses": total_bonus
    }


@router.post(
    "/{contest_id}/finalize",
    summary="Finalize contest (Admin)",
    description="Calculate final ranks, distribute prizes, update contest status"
)
async def finalize_contest(
    contest_id: str,
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    contest = await db.contests.find_one({"id": contest_id})
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")

    if contest["status"] == "completed":
        return {"message": "Contest already finalized"}

    # Check all questions are resolved before finalizing
    template = await db.templates.find_one({"id": contest.get("template_id")}, {"_id": 0, "question_ids": 1})
    if template:
        qids = template.get("question_ids", [])
        resolved_count = await db.question_results.count_documents({
            "match_id": contest["match_id"],
            "question_id": {"$in": qids}
        })
        if resolved_count < len(qids):
            raise HTTPException(
                status_code=400,
                detail=f"Cannot finalize: {len(qids) - resolved_count}/{len(qids)} questions still unresolved. Resolve all questions first."
            )

    now = utc_now().isoformat()

    # 1. Get all entries sorted by total_points DESC, submission_time ASC (tiebreaker)
    entries_cursor = db.contest_entries.find(
        {"contest_id": contest_id}
    ).sort([("total_points", -1), ("submission_time", 1)])
    entries = await entries_cursor.to_list(length=10000)

    # 2. Calculate prizes - 50/30/20 of total pool
    entry_fee = contest.get("entry_fee", 1000)
    num_entries = len(entries)
    total_pool = entry_fee * num_entries

    # Dynamic prize: 1st=50%, 2nd=30%, 3rd=20%
    prize_map = {
        1: int(total_pool * 0.50),
        2: int(total_pool * 0.30),
        3: int(total_pool * 0.20),
    }

    total_prizes = 0
    bulk_ops = []

    from pymongo import UpdateOne
    for rank, entry in enumerate(entries, 1):
        prize = prize_map.get(rank, 0)

        total_prizes += prize
        bulk_ops.append(UpdateOne(
            {"_id": entry["_id"]},
            {"$set": {"final_rank": rank, "prize_won": prize, "updated_at": now}}
        ))

        # Credit prize to user's wallet
        if prize > 0:
            user = await db.users.find_one({"id": entry["user_id"]})
            if user:
                new_balance = user["coins_balance"] + prize
                await db.users.update_one(
                    {"id": entry["user_id"]},
                    {"$inc": {"coins_balance": prize, "contests_won": 1}}
                )
                await db.wallet_transactions.insert_one({
                    "id": generate_id(),
                    "user_id": entry["user_id"],
                    "type": "credit",
                    "amount": prize,
                    "reason": "contest_win",
                    "reference_id": contest_id,
                    "balance_after": new_balance,
                    "description": f"Rank #{rank} in {contest['name']} - Prize: {prize} coins",
                    "created_at": now,
                    "updated_at": now
                })

    if bulk_ops:
        await db.contest_entries.bulk_write(bulk_ops)

    # 3. Update all participants' matches_played
    user_ids = [e["user_id"] for e in entries]
    if user_ids:
        await db.users.update_many(
            {"id": {"$in": user_ids}},
            {"$inc": {"matches_played": 1}}
        )

    # 4. Mark contest as completed
    await db.contests.update_one(
        {"id": contest_id},
        {"$set": {"status": "completed", "updated_at": now}}
    )

    # Enrich top 3 with usernames
    top_3_users = []
    for i, e in enumerate(entries[:3]):
        u = await db.users.find_one({"id": e["user_id"]}, {"_id": 0, "username": 1})
        top_3_users.append({
            "rank": i + 1,
            "user_id": e["user_id"],
            "username": u.get("username", "Unknown") if u else "Unknown",
            "team_name": e.get("team_name", ""),
            "points": e["total_points"],
            "prize_won": e.get("prize_won", 0)
        })

    return {
        "contest_id": contest_id,
        "total_entries": len(entries),
        "prizes_distributed": total_prizes,
        "status": "completed",
        "top_3": top_3_users
    }


# ==================== LEADERBOARD ====================

@router.get(
    "/{contest_id}/leaderboard",
    summary="Contest leaderboard",
    description="Get leaderboard for a contest (ranked by points, tiebreak by submission time)"
)
async def get_leaderboard(
    contest_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100)
):
    contest = await db.contests.find_one({"id": contest_id}, {"_id": 0, "id": 1, "name": 1, "current_participants": 1, "prize_pool": 1})
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")

    # Get entries sorted
    cursor = db.contest_entries.find(
        {"contest_id": contest_id},
        {"_id": 0, "user_id": 1, "team_name": 1, "total_points": 1, "submission_time": 1, "final_rank": 1, "prize_won": 1}
    ).sort([("total_points", -1), ("submission_time", 1)]).limit(limit)
    entries = await cursor.to_list(length=limit)

    # Enrich with usernames
    user_ids = [e["user_id"] for e in entries]
    if user_ids:
        users_cursor = db.users.find(
            {"id": {"$in": user_ids}},
            {"_id": 0, "id": 1, "username": 1, "avatar_url": 1}
        )
        users = await users_cursor.to_list(length=len(user_ids))
        user_map = {u["id"]: u for u in users}
    else:
        user_map = {}

    leaderboard = []
    for rank, entry in enumerate(entries, 1):
        u = user_map.get(entry["user_id"], {})
        leaderboard.append({
            "rank": entry.get("final_rank") or rank,
            "user_id": entry["user_id"],
            "username": u.get("username", "Unknown"),
            "avatar_url": u.get("avatar_url"),
            "team_name": entry.get("team_name", ""),
            "total_points": entry["total_points"],
            "prize_won": entry.get("prize_won", 0)
        })

    return {
        "contest_id": contest_id,
        "contest_name": contest.get("name", ""),
        "total_participants": contest.get("current_participants", 0),
        "prize_pool": contest.get("prize_pool", 0),
        "leaderboard": leaderboard
    }


@router.get(
    "/{contest_id}/leaderboard/me",
    summary="My position in leaderboard"
)
async def get_my_leaderboard_position(
    contest_id: str,
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    entry = await db.contest_entries.find_one(
        {"contest_id": contest_id, "user_id": current_user.id},
        {"_id": 0}
    )
    if not entry:
        raise HTTPException(status_code=404, detail="No entry found")

    # Calculate rank
    rank_query = {
        "contest_id": contest_id,
        "total_points": {"$gt": entry["total_points"]}
    }
    # Only use submission_time tiebreaker if both have it
    if entry.get("submission_time"):
        higher_count = await db.contest_entries.count_documents({
            "contest_id": contest_id,
            "$or": [
                {"total_points": {"$gt": entry["total_points"]}},
                {
                    "total_points": entry["total_points"],
                    "submission_time": {"$ne": None, "$lt": entry["submission_time"]}
                }
            ]
        })
    else:
        higher_count = await db.contest_entries.count_documents(rank_query)

    return {
        "rank": higher_count + 1,
        "total_points": entry["total_points"],
        "team_name": entry.get("team_name", ""),
        "predictions_count": len(entry.get("predictions", [])),
        "prize_won": entry.get("prize_won", 0)
    }



# ==================== USER ANSWER DETAIL ====================

@router.get(
    "/{contest_id}/leaderboard/{user_id}",
    summary="View user's answers in a contest",
    description="Get a user's predictions with question details for leaderboard drill-down"
)
async def get_user_answers(
    contest_id: str,
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    entry = await db.contest_entries.find_one(
        {"contest_id": contest_id, "user_id": user_id},
        {"_id": 0}
    )
    if not entry:
        raise HTTPException(status_code=404, detail="User entry not found")

    # Get user info
    user = await db.users.find_one(
        {"id": user_id},
        {"_id": 0, "username": 1, "avatar_url": 1, "rank_title": 1}
    )

    # Get question details for each prediction
    qids = [p["question_id"] for p in entry.get("predictions", [])]
    questions = []
    if qids:
        q_cursor = db.questions.find(
            {"id": {"$in": qids}},
            {"_id": 0, "id": 1, "question_text_en": 1, "question_text_hi": 1, "category": 1, "points": 1, "options": 1}
        )
        q_list = await q_cursor.to_list(length=len(qids))
        q_map = {q["id"]: q for q in q_list}

        for pred in entry.get("predictions", []):
            q = q_map.get(pred["question_id"], {})
            questions.append({
                "question_text_hi": q.get("question_text_hi", ""),
                "question_text_en": q.get("question_text_en", ""),
                "category": q.get("category", ""),
                "points": q.get("points", 0),
                "selected_option": pred.get("selected_option", ""),
                "is_correct": pred.get("is_correct"),
                "points_earned": pred.get("points_earned", 0),
                "options": q.get("options", [])
            })

    # Get question results for this contest's match
    contest = await db.contests.find_one({"id": contest_id}, {"_id": 0, "match_id": 1, "name": 1})
    results_map = {}
    if contest:
        result_cursor = db.question_results.find(
            {"match_id": contest["match_id"]},
            {"_id": 0, "question_id": 1, "correct_option": 1}
        )
        results = await result_cursor.to_list(length=100)
        results_map = {r["question_id"]: r["correct_option"] for r in results}

    # Enrich with correct option
    for i, pred in enumerate(entry.get("predictions", [])):
        if pred["question_id"] in results_map:
            questions[i]["correct_option"] = results_map[pred["question_id"]]

    return {
        "user_id": user_id,
        "username": user.get("username", "Unknown") if user else "Unknown",
        "avatar_url": user.get("avatar_url") if user else None,
        "rank_title": user.get("rank_title", "Rookie") if user else "Rookie",
        "team_name": entry.get("team_name", ""),
        "total_points": entry.get("total_points", 0),
        "final_rank": entry.get("final_rank"),
        "prize_won": entry.get("prize_won", 0),
        "predictions": questions,
        "contest_name": contest.get("name", "") if contest else ""
    }


# ==================== GLOBAL PREDICTION ACCURACY LEADERBOARD ====================

@router.get(
    "/global/prediction-leaderboard",
    summary="Global Prediction Accuracy Leaderboard",
    description="Ranks ALL users by total correct answers across ALL contests, irrespective of wins."
)
async def global_prediction_leaderboard(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Aggregates correct predictions across every contest for every user.
    Returns ranked list with badge info (Pink Diamond #1, Gold #2, Silver #3, Blue Crystal #4+).
    """
    pipeline = [
        # Unwind predictions array
        {"$unwind": "$predictions"},
        # Only count settled predictions (is_correct not null)
        {"$match": {"predictions.is_correct": {"$ne": None}}},
        # Group by user
        {"$group": {
            "_id": "$user_id",
            "total_correct": {"$sum": {"$cond": ["$predictions.is_correct", 1, 0]}},
            "total_attempted": {"$sum": 1},
            "total_points_earned": {"$sum": "$predictions.points_earned"},
            "contests_played": {"$addToSet": "$contest_id"},
        }},
        # Add computed fields
        {"$addFields": {
            "accuracy_pct": {
                "$round": [{"$multiply": [{"$divide": ["$total_correct", {"$max": ["$total_attempted", 1]}]}, 100]}, 1]
            },
            "contests_count": {"$size": "$contests_played"},
        }},
        # Sort by total_correct DESC, then accuracy DESC
        {"$sort": {"total_correct": -1, "accuracy_pct": -1}},
        {"$limit": limit},
    ]

    results = await db.contest_entries.aggregate(pipeline).to_list(limit)

    # Fetch user details
    user_ids = [r["_id"] for r in results]
    users_cursor = db.users.find(
        {"id": {"$in": user_ids}},
        {"_id": 0, "id": 1, "username": 1, "phone": 1, "avatar_url": 1}
    )
    users_list = await users_cursor.to_list(len(user_ids))
    users_map = {u["id"]: u for u in users_list}

    leaderboard = []
    for rank, r in enumerate(results, 1):
        u = users_map.get(r["_id"], {})
        badge = "pink_diamond" if rank == 1 else "gold" if rank == 2 else "silver" if rank == 3 else "blue_crystal"
        leaderboard.append({
            "rank": rank,
            "user_id": r["_id"],
            "username": u.get("username", "Unknown"),
            "avatar_url": u.get("avatar_url"),
            "total_correct": r["total_correct"],
            "total_attempted": r["total_attempted"],
            "accuracy_pct": r["accuracy_pct"],
            "total_points_earned": r["total_points_earned"],
            "contests_count": r["contests_count"],
            "badge": badge,
        })

    return {"leaderboard": leaderboard, "total_ranked": len(leaderboard)}


@router.get(
    "/global/my-badge",
    summary="Get current user's prediction badge",
    description="Returns the user's global prediction rank, badge, accuracy stats."
)
async def get_my_badge(
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get the current user's global prediction accuracy badge."""
    user_id = current_user.id

    # Get this user's stats
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$unwind": "$predictions"},
        {"$match": {"predictions.is_correct": {"$ne": None}}},
        {"$group": {
            "_id": "$user_id",
            "total_correct": {"$sum": {"$cond": ["$predictions.is_correct", 1, 0]}},
            "total_attempted": {"$sum": 1},
            "total_points_earned": {"$sum": "$predictions.points_earned"},
            "contests_played": {"$addToSet": "$contest_id"},
        }},
    ]
    user_stats = await db.contest_entries.aggregate(pipeline).to_list(1)

    if not user_stats:
        return {
            "rank": None,
            "badge": None,
            "total_correct": 0,
            "total_attempted": 0,
            "accuracy_pct": 0,
            "total_points_earned": 0,
            "contests_count": 0,
        }

    stats = user_stats[0]
    total_correct = stats["total_correct"]
    total_attempted = stats["total_attempted"]
    accuracy_pct = round((total_correct / max(total_attempted, 1)) * 100, 1)

    # Count how many users have more correct answers
    rank_pipeline = [
        {"$unwind": "$predictions"},
        {"$match": {"predictions.is_correct": {"$ne": None}}},
        {"$group": {
            "_id": "$user_id",
            "total_correct": {"$sum": {"$cond": ["$predictions.is_correct", 1, 0]}},
        }},
        {"$match": {"total_correct": {"$gt": total_correct}}},
        {"$count": "above"},
    ]
    above = await db.contest_entries.aggregate(rank_pipeline).to_list(1)
    rank = (above[0]["above"] if above else 0) + 1

    badge = "pink_diamond" if rank == 1 else "gold" if rank == 2 else "silver" if rank == 3 else "blue_crystal"

    return {
        "rank": rank,
        "badge": badge,
        "total_correct": total_correct,
        "total_attempted": total_attempted,
        "accuracy_pct": accuracy_pct,
        "total_points_earned": stats["total_points_earned"],
        "contests_count": len(stats["contests_played"]),
    }


# ==================== PREDICTION STREAK ====================

@router.get(
    "/global/top-streak",
    summary="Top prediction streak holders",
    description="Returns users with the highest current active prediction streaks."
)
async def get_top_streaks(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get top users by active prediction streak (current hot streaks)."""
    cursor = db.users.find(
        {"prediction_streak": {"$gte": 1}},
        {"_id": 0, "id": 1, "username": 1, "avatar_url": 1, "prediction_streak": 1, "max_prediction_streak": 1}
    ).sort("prediction_streak", -1).limit(limit)
    users = await cursor.to_list(length=limit)

    streaks = []
    for rank, u in enumerate(users, 1):
        streaks.append({
            "rank": rank,
            "user_id": u["id"],
            "username": u.get("username", "Unknown"),
            "avatar_url": u.get("avatar_url"),
            "current_streak": u.get("prediction_streak", 0),
            "max_streak": u.get("max_prediction_streak", 0),
            "is_hot": u.get("prediction_streak", 0) >= 5,
        })

    return {"streaks": streaks, "total": len(streaks)}


@router.get(
    "/global/my-streak",
    summary="Get current user's prediction streak",
    description="Returns the user's current and max prediction streak with multiplier info."
)
async def get_my_streak(
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get the current user's prediction streak status."""
    user = await db.users.find_one(
        {"id": current_user.id},
        {"_id": 0, "prediction_streak": 1, "max_prediction_streak": 1}
    )
    if not user:
        return {"current_streak": 0, "max_streak": 0, "is_hot": False, "multiplier": 1, "next_milestone": 5}

    current = user.get("prediction_streak", 0)
    max_s = user.get("max_prediction_streak", 0)
    is_hot = current >= 5

    if current >= 10:
        multiplier = 4
        next_milestone = None  # Already at max
    elif current >= 5:
        multiplier = 2
        next_milestone = 10
    else:
        multiplier = 1
        next_milestone = 5

    return {
        "current_streak": current,
        "max_streak": max_s,
        "is_hot": is_hot,
        "multiplier": multiplier,
        "next_milestone": next_milestone,
        "streak_to_next": (next_milestone - current) if next_milestone else 0,
    }
