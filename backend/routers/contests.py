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
    predictions: list[PredictionItem] = Field(..., min_length=1, max_length=15)


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

    if contest["status"] != "open":
        raise HTTPException(status_code=400, detail="Contest is not open for joining")

    # Check lock time
    lock_time = contest.get("lock_time", "")
    if lock_time:
        lt = datetime.fromisoformat(lock_time.replace('Z', '+00:00')) if isinstance(lock_time, str) else lock_time
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

    # 4. Deduct entry fee (atomic)
    if entry_fee > 0:
        new_balance = user["coins_balance"] - entry_fee
        await db.users.update_one(
            {"id": current_user.id, "coins_balance": {"$gte": entry_fee}},
            {"$inc": {"coins_balance": -entry_fee}}
        )
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
    await db.contest_entries.insert_one(entry)

    # 6. Increment participant count
    await db.contests.update_one(
        {"id": contest_id},
        {"$inc": {"current_participants": 1}, "$set": {"updated_at": now}}
    )

    del entry["_id"]
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
        is_locked = datetime.now(timezone.utc) >= lt

    return {
        "contest_id": contest_id,
        "template_name": template.get("name", ""),
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

    # 2. Check lock time
    lock_time = contest.get("lock_time", "")
    if lock_time:
        lt = datetime.fromisoformat(lock_time.replace('Z', '+00:00')) if isinstance(lock_time, str) else lock_time
        if datetime.now(timezone.utc) >= lt:
            raise HTTPException(status_code=400, detail="Contest is locked. Predictions cannot be modified")

    # 3. Verify user has joined
    entry = await db.contest_entries.find_one(
        {"contest_id": contest_id, "user_id": current_user.id}
    )
    if not entry:
        raise HTTPException(status_code=403, detail="You haven't joined this contest. Join first.")

    # 4. Validate question IDs belong to contest template
    template = await db.templates.find_one({"id": contest.get("template_id")}, {"_id": 0, "question_ids": 1})
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
    ).sort("created_at", -1).skip(skip).limit(limit)
    entries = await entry_cursor.to_list(length=limit)

    total = await db.contest_entries.count_documents({"user_id": current_user.id})

    # Enrich with contest + match data
    result = []
    for entry in entries:
        contest = await db.contests.find_one(
            {"id": entry["contest_id"]},
            {"_id": 0, "name": 1, "status": 1, "match_id": 1, "entry_fee": 1, "prize_pool": 1, "current_participants": 1}
        )
        if not contest:
            continue

        if contest_status and contest.get("status") != contest_status:
            continue

        match = await db.matches.find_one(
            {"id": contest.get("match_id")},
            {"_id": 0, "team_a": 1, "team_b": 1, "status": 1, "start_time": 1}
        )

        result.append({
            "entry": entry,
            "contest": contest,
            "match": match
        })

    return {"my_contests": result, "total": total, "page": page, "has_more": (page * limit) < total}


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

    for entry in entries:
        for i, pred in enumerate(entry.get("predictions", [])):
            if pred["question_id"] == data.question_id:
                is_correct = pred["selected_option"] == data.correct_option
                earned = points_value if is_correct else 0

                if is_correct:
                    correct_count += 1
                else:
                    wrong_count += 1

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
        "points_value": points_value
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

    now = utc_now().isoformat()

    # 1. Get all entries sorted by total_points DESC, submission_time ASC (tiebreaker)
    entries_cursor = db.contest_entries.find(
        {"contest_id": contest_id}
    ).sort([("total_points", -1), ("submission_time", 1)])
    entries = await entries_cursor.to_list(length=10000)

    # 2. Assign ranks
    prize_dist = contest.get("prize_distribution", [])
    total_prizes = 0
    bulk_ops = []

    from pymongo import UpdateOne
    for rank, entry in enumerate(entries, 1):
        prize = 0
        for pd in prize_dist:
            if pd["rank_start"] <= rank <= pd["rank_end"]:
                prize = pd["prize"]
                break

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

    return {
        "contest_id": contest_id,
        "total_entries": len(entries),
        "prizes_distributed": total_prizes,
        "status": "completed",
        "top_3": [
            {"rank": i+1, "user_id": e["user_id"], "team_name": e.get("team_name", ""), "points": e["total_points"]}
            for i, e in enumerate(entries[:3])
        ]
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
    higher_count = await db.contest_entries.count_documents({
        "contest_id": contest_id,
        "$or": [
            {"total_points": {"$gt": entry["total_points"]}},
            {"total_points": entry["total_points"], "submission_time": {"$lt": entry.get("submission_time")}}
        ]
    })

    return {
        "rank": higher_count + 1,
        "total_points": entry["total_points"],
        "team_name": entry.get("team_name", ""),
        "predictions_count": len(entry.get("predictions", [])),
        "prize_won": entry.get("prize_won", 0)
    }
