"""
CrickPredict - Fantasy Cricket Prediction Platform
Main FastAPI Application Entry Point

Architecture: Clean Architecture with Repository Pattern
- Routers: HTTP endpoints (thin layer)
- Services: Business logic
- Repositories: Data access
- Models: Pydantic schemas (canonical data)
- Core: Shared utilities (database, redis, security)
"""
import sys
import os
import uuid
import time as time_module
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from core.database import db_manager
from core.logging import setup_logging, get_logger
from core.exceptions import CrickPredictException

# Import routers
from routers.health import router as health_router
from routers.auth import router as auth_router
from routers.user import router as user_router
from routers.wallet import router as wallet_router
from routers.admin import router as admin_router
from routers.matches import router as matches_router
from routers.contests import router as contests_router
from routers.cricket import router as cricket_router
from routers.ipl_router import router as ipl_router

# Setup logging
setup_logging()
logger = get_logger(__name__)


# ==================== MIDDLEWARE ====================

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Inject unique request ID for distributed tracing."""
    
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class ResponseTimingMiddleware(BaseHTTPMiddleware):
    """Measure and log API response times."""
    
    async def dispatch(self, request: Request, call_next):
        start = time_module.perf_counter()
        response = await call_next(request)
        duration_ms = (time_module.perf_counter() - start) * 1000
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
        if duration_ms > 200:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} took {duration_ms:.2f}ms"
            )
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add comprehensive security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https: wss: ws:; frame-ancestors 'none'"
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


class RateLimitHeadersMiddleware(BaseHTTPMiddleware):
    """Inject rate limit info headers from request state."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if hasattr(request.state, 'rate_limit_remaining'):
            response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_limit)
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)
            response.headers["X-RateLimit-Window"] = str(request.state.rate_limit_window)
        return response


class RequestBodyLimitMiddleware(BaseHTTPMiddleware):
    """Reject request bodies larger than MAX_BODY_SIZE to prevent DoS."""
    MAX_BODY_SIZE = 1 * 1024 * 1024  # 1 MB
    
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.MAX_BODY_SIZE:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=413,
                content={"error": "PAYLOAD_TOO_LARGE", "message": f"Request body exceeds {self.MAX_BODY_SIZE // 1024}KB limit"}
            )
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    try:
        # Connect to databases
        await db_manager.connect()
        
        # Connect to Redis (non-critical — falls back gracefully)
        from services.redis_cache import init_redis, close_redis
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        await init_redis(redis_url)
        
        # Create indexes (idempotent)
        await create_indexes()
        
        # Seed super admin (idempotent)
        await seed_super_admin()
        
        # Seed IPL encyclopedia data (idempotent)
        try:
            from services.ipl_data_seeder import seed_ipl_data
            ipl_result = await seed_ipl_data(db_manager.db)
            logger.info(f"IPL data seeded: {ipl_result}")
        except Exception as e:
            logger.warning(f"IPL data seeding failed (non-critical): {e}")

        # Auto-sync IPL 2026 schedule from CricketData.org on startup
        try:
            await _auto_sync_ipl_schedule(db_manager.db)
        except Exception as e:
            logger.warning(f"IPL schedule auto-sync failed (non-critical): {e}")
        
        logger.info("Application startup complete")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    try:
        from services.redis_cache import close_redis
        await close_redis()
    except Exception:
        pass
    await db_manager.disconnect()
    logger.info("Application shutdown complete")


async def create_indexes():
    """Create MongoDB indexes for optimal query performance using bulk operations."""
    db = db_manager.db
    
    from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT
    
    # Users collection indexes
    await db.users.create_indexes([
        IndexModel([("id", ASCENDING)], unique=True),
        IndexModel([("phone", ASCENDING)], unique=True),
        IndexModel([("referral_code", ASCENDING)], unique=True),
        IndexModel([("username", TEXT)]),
    ])
    
    # Matches collection indexes — optimized for hot queries
    await db.matches.create_indexes([
        IndexModel([("id", ASCENDING)], unique=True),
        IndexModel([("external_match_id", ASCENDING)], sparse=True),
        IndexModel([("cricketdata_id", ASCENDING)], sparse=True),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("start_time", ASCENDING)]),
        IndexModel([("status", ASCENDING), ("start_time", ASCENDING)]),
        IndexModel([("status", ASCENDING), ("start_time", DESCENDING)]),
        IndexModel([("status", ASCENDING), ("manual_override", ASCENDING), ("start_time", ASCENDING)]),
    ])
    
    # Contests collection indexes — optimized for match lookup + status filtering
    await db.contests.create_indexes([
        IndexModel([("id", ASCENDING)], unique=True),
        IndexModel([("match_id", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("match_id", ASCENDING), ("status", ASCENDING)]),
        IndexModel([("lock_time", ASCENDING)]),
        IndexModel([("match_id", ASCENDING), ("manual_override", ASCENDING), ("status", ASCENDING)]),
        IndexModel([("status", ASCENDING), ("created_at", DESCENDING)]),
    ])
    
    # Contest entries collection indexes
    await db.contest_entries.create_indexes([
        IndexModel([("id", ASCENDING)], unique=True),
        IndexModel([("contest_id", ASCENDING), ("user_id", ASCENDING)], unique=True),
        IndexModel([("user_id", ASCENDING)]),
        IndexModel([("contest_id", ASCENDING), ("total_points", DESCENDING)]),
    ])
    
    # Questions collection indexes
    await db.questions.create_indexes([
        IndexModel([("id", ASCENDING)], unique=True),
        IndexModel([("category", ASCENDING)]),
        IndexModel([("is_active", ASCENDING)]),
        IndexModel([("is_active", ASCENDING), ("category", ASCENDING)]),
    ])
    
    # Templates collection indexes
    await db.templates.create_indexes([
        IndexModel([("id", ASCENDING)], unique=True),
        IndexModel([("match_type", ASCENDING)]),
        IndexModel([("is_active", ASCENDING)]),
    ])
    
    # Question results collection indexes
    await db.question_results.create_indexes([
        IndexModel([("id", ASCENDING)], unique=True),
        IndexModel([("match_id", ASCENDING), ("question_id", ASCENDING)], unique=True),
    ])
    
    # Wallet transactions collection indexes
    await db.wallet_transactions.create_indexes([
        IndexModel([("id", ASCENDING)], unique=True),
        IndexModel([("user_id", ASCENDING)]),
        IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
        IndexModel([("user_id", ASCENDING), ("reason", ASCENDING)]),
    ])

    # Users collection indexes
    await db.users.create_indexes([
        IndexModel([("id", ASCENDING)], unique=True),
        IndexModel([("phone", ASCENDING)], unique=True),
        IndexModel([("role", ASCENDING)]),
    ])

    # IPL data indexes
    await db.ipl_players.create_indexes([
        IndexModel([("name", ASCENDING)]),
        IndexModel([("current_team", ASCENDING)]),
        IndexModel([("role", ASCENDING)]),
    ])
    await db.ipl_records.create_indexes([
        IndexModel([("category", ASCENDING)]),
    ])
    
    logger.info("Database indexes created/verified (bulk)")

    # API Cache indexes for fast lookups
    await db.api_cache.create_indexes([
        IndexModel([("cache_type", ASCENDING), ("cache_key", ASCENDING)], unique=True),
        IndexModel([("cached_at", ASCENDING)]),
    ])



async def _auto_sync_ipl_schedule(db):
    """Auto-sync IPL 2026 schedule on startup using series_info API."""
    from services.api_cache import cached_cricket
    from services.cricket_data import _get_short_name, _align_team_info, _normalize_score
    from models.schemas import generate_id, utc_now

    IPL_SERIES_ID = "87c62aac-bc3c-4738-ab93-19da0690488f"

    series_data = await cached_cricket.get_series_info(db, IPL_SERIES_ID)
    if not series_data:
        logger.warning("Auto-sync: Could not fetch IPL schedule")
        return

    match_list = series_data.get("matchList", [])
    now = utc_now().isoformat()
    created = 0
    updated = 0

    for api_match in match_list:
        cd_id = api_match.get("id", "")
        if not cd_id:
            continue

        teams = api_match.get("teams", [])
        team_info = api_match.get("teamInfo", [])
        match_ended = api_match.get("matchEnded", False)
        match_started = api_match.get("matchStarted", False)
        status_text = api_match.get("status", "")
        # Fix false "live" detection — API sometimes returns matchStarted=true for upcoming matches
        if match_started and not match_ended and "match starts at" in status_text.lower():
            m_status = "upcoming"
        else:
            m_status = "completed" if match_ended else ("live" if match_started else "upcoming")

        # ALIGN teamInfo to teams[] order (fixes random API swap bug)
        if len(team_info) >= 2 and len(teams) >= 2:
            team_a_info, team_b_info = _align_team_info(teams, team_info)
            t1_name = team_a_info.get("name", teams[0])
            t1_short = _get_short_name(team_a_info.get("shortname", t1_name))
            t1_img = team_a_info.get("img", "")
            t2_name = team_b_info.get("name", teams[1])
            t2_short = _get_short_name(team_b_info.get("shortname", t2_name))
            t2_img = team_b_info.get("img", "")
        else:
            t1_name = teams[0] if teams else "?"
            t2_name = teams[1] if len(teams) > 1 else "?"
            t1_short = _get_short_name(t1_name)
            t2_short = _get_short_name(t2_name)
            t1_img = ""
            t2_img = ""

        scores = []
        for s in api_match.get("score", []):
            scores.append(_normalize_score({
                "inning": s.get("inning", ""),
                "r": s.get("r", 0), "w": s.get("w", 0), "o": s.get("o", 0),
            }))

        # Check if exists
        existing = await db.matches.find_one(
            {"$or": [{"cricketdata_id": cd_id}, {"external_match_id": cd_id}]}, {"_id": 0}
        )
        if not existing:
            # Try team name match
            existing = await db.matches.find_one(
                {"team_a.short_name": {"$in": [t1_short, t2_short]},
                 "team_b.short_name": {"$in": [t1_short, t2_short]},
                 "cricketdata_id": {"$in": [None, "", "NONE"]}}, {"_id": 0}
            )
            if existing:
                await db.matches.update_one(
                    {"id": existing["id"]}, {"$set": {"cricketdata_id": cd_id, "external_match_id": cd_id}}
                )

        if existing:
            updates = {"updated_at": now, "cricketdata_id": cd_id, "status_text": api_match.get("status", "")}
            old_status = existing.get("status", "upcoming")
            if m_status != old_status:
                VALID = {"upcoming": ["live", "completed"], "live": ["completed"]}
                if m_status in VALID.get(old_status, []):
                    updates["status"] = m_status
            if scores:
                existing_scores = existing.get("live_score", {}).get("scores", [])
                existing_has_real = any(s.get("r", 0) > 0 or s.get("runs", 0) > 0 for s in existing_scores)
                new_has_real = any(s.get("r", 0) > 0 or s.get("runs", 0) > 0 for s in scores)
                if new_has_real or not existing_has_real:
                    updates["live_score"] = {"scores": scores, "updated_at": now}
            if not existing.get("team_a", {}).get("img") and t1_img:
                updates["team_a.img"] = t1_img
            if not existing.get("team_b", {}).get("img") and t2_img:
                updates["team_b.img"] = t2_img
            await db.matches.update_one({"id": existing["id"]}, {"$set": updates})
            updated += 1
        else:
            match_doc = {
                "id": generate_id(), "external_match_id": cd_id, "cricketdata_id": cd_id,
                "source": "cricketdata",
                "team_a": {"name": t1_name, "short_name": t1_short, "img": t1_img},
                "team_b": {"name": t2_name, "short_name": t2_short, "img": t2_img},
                "match_type": api_match.get("matchType", "t20"),
                "venue": api_match.get("venue", ""),
                "start_time": api_match.get("dateTimeGMT", now),
                "status": m_status, "status_text": api_match.get("status", ""),
                "live_score": {"scores": scores, "updated_at": now} if scores else None,
                "templates_assigned": [], "created_at": now, "updated_at": now,
            }
            await db.matches.insert_one(match_doc)
            created += 1

    logger.info(f"Auto-sync IPL schedule: {created} created, {updated} updated (total {len(match_list)} matches)")

    # Phase 2: For completed matches WITHOUT real scores, fetch from match_scorecard API
    # This catches: no live_score, empty scores array, or scores where both r AND runs are 0/missing
    completed_no_score = db.matches.find({
        "status": "completed",
        "cricketdata_id": {"$nin": [None, ""]},
        "$or": [
            {"live_score": None},
            {"live_score.scores": {"$size": 0}},
            {"live_score.scores": {"$exists": False}},
            # r field missing or 0 for both innings
            {"$and": [
                {"$or": [{"live_score.scores.0.r": 0}, {"live_score.scores.0.r": {"$exists": False}}]},
                {"$or": [{"live_score.scores.0.runs": 0}, {"live_score.scores.0.runs": {"$exists": False}}]},
            ]},
        ]
    }, {"_id": 0, "id": 1, "cricketdata_id": 1, "team_a.short_name": 1, "team_b.short_name": 1})

    scores_fetched = 0
    async for match in completed_no_score:
        cd_id = match.get("cricketdata_id")
        if not cd_id:
            continue
        try:
            sc_data = await cached_cricket.get_scorecard(db, cd_id)
            if sc_data:
                scorecard = sc_data.get("scorecard", [])
                real_scores = []
                for inn in scorecard:
                    inning_name = inn.get("inning", "")
                    batting = inn.get("batting", [])
                    total_runs = sum(int(b.get("r", 0)) for b in batting)
                    total_wickets = len([b for b in batting if b.get("dismissal") and b["dismissal"] != "not out"])
                    total_overs = inn.get("totals", {}).get("O", "0")
                    extras = inn.get("extras", {}).get("t", 0) if isinstance(inn.get("extras"), dict) else 0
                    real_scores.append(_normalize_score({
                        "inning": inning_name,
                        "r": total_runs + extras,
                        "w": total_wickets,
                        "o": total_overs,
                    }))
                if real_scores and any(s["r"] > 0 for s in real_scores):
                    await db.matches.update_one(
                        {"id": match["id"]},
                        {"$set": {
                            "live_score": {"scores": real_scores, "updated_at": now},
                            "match_winner": sc_data.get("matchWinner", ""),
                        }}
                    )
                    ta = match.get("team_a", {}).get("short_name", "?")
                    tb = match.get("team_b", {}).get("short_name", "?")
                    score_strs = [f'{s["r"]}/{s["w"]}' for s in real_scores]
                    logger.info(f"Fetched scores for {ta} vs {tb}: {score_strs}")
                    scores_fetched += 1
        except Exception as e:
            logger.warning(f"Score fetch failed for {cd_id}: {e}")

    if scores_fetched:
        logger.info(f"Auto-sync Phase 2: Fetched scores for {scores_fetched} completed matches")



async def seed_super_admin():
    """Ensure super admin user exists (idempotent)."""
    db = db_manager.db
    SUPER_ADMIN_PHONE = "7004186276"
    SUPER_ADMIN_PIN = "5524"
    
    existing = await db.users.find_one({"phone": SUPER_ADMIN_PHONE})
    if existing:
        updates = {}
        if not existing.get("is_admin"):
            updates["is_admin"] = True
        if existing.get("username", "").startswith("Player"):
            updates["username"] = "SuperAdmin"
        if existing.get("coins_balance", 0) < 100000:
            updates["coins_balance"] = 100000
        if updates:
            await db.users.update_one({"phone": SUPER_ADMIN_PHONE}, {"$set": updates})
            logger.info(f"Updated super admin {SUPER_ADMIN_PHONE}: {list(updates.keys())}")
        return
    
    from core.security import jwt_manager
    from models.schemas import generate_id, generate_referral_code, utc_now
    
    pin_hash = jwt_manager.hash_pin(SUPER_ADMIN_PIN)
    user_doc = {
        "id": generate_id(),
        "phone": SUPER_ADMIN_PHONE,
        "pin_hash": pin_hash,
        "username": "SuperAdmin",
        "avatar_url": None,
        "coins_balance": 100000,
        "rank_title": "GOAT",
        "total_points": 0,
        "matches_played": 0,
        "contests_won": 0,
        "referral_code": generate_referral_code(),
        "referred_by": None,
        "daily_streak": 0,
        "last_daily_claim": None,
        "is_banned": False,
        "is_admin": True,
        "failed_login_attempts": 0,
        "locked_until": None,
        "created_at": utc_now().isoformat(),
        "updated_at": utc_now().isoformat()
    }
    await db.users.insert_one(user_doc)
    logger.info(f"Super admin created: {SUPER_ADMIN_PHONE}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Fantasy Cricket Prediction Platform - Predict and Win Virtual Coins!",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)


# Global exception handler
@app.exception_handler(CrickPredictException)
async def crickpredict_exception_handler(request: Request, exc: CrickPredictException):
    """Handle all CrickPredict custom exceptions."""
    logger.warning(f"API Error: {exc.code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.code,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "details": {}
        }
    )


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip Compression (min 500 bytes)
app.add_middleware(GZipMiddleware, minimum_size=500)

# Request body size limit (1MB)
app.add_middleware(RequestBodyLimitMiddleware)

# Security headers (CSP, X-Frame-Options, etc.)
app.add_middleware(SecurityHeadersMiddleware)

# Rate limit headers
app.add_middleware(RateLimitHeadersMiddleware)

# Request ID for distributed tracing
app.add_middleware(RequestIDMiddleware)

# Response timing
app.add_middleware(ResponseTimingMiddleware)


# Include routers with /api prefix
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(wallet_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(matches_router, prefix="/api")
app.include_router(contests_router, prefix="/api")
app.include_router(cricket_router, prefix="/api")
app.include_router(ipl_router, prefix="/api")

from routers.notifications import router as notifications_router
app.include_router(notifications_router, prefix="/api")


# Root endpoint
@app.get("/api")
async def root():
    """API root endpoint."""
    from services.socket_manager import get_socket_status
    from services.redis_cache import get_cache_stats
    cache = await get_cache_stats()
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs" if settings.DEBUG else "disabled",
        "socket": get_socket_status(),
        "cache": cache,
    }


# ==================== SOCKET.IO ASGI APP ====================
# Wraps FastAPI with Socket.IO for WebSocket support
# The combined_app is the top-level ASGI entrypoint used by uvicorn
import socketio as _socketio_module
from services.socket_manager import sio

combined_app = _socketio_module.ASGIApp(
    sio,
    app,
    socketio_path='api/socket.io'
)
