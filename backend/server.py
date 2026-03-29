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
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from core.database import db_manager
from core.logging import setup_logging, get_logger
from core.exceptions import CrickPredictException

# Import routers
from routers.health import router as health_router
from routers.auth import router as auth_router

# Setup logging
setup_logging()
logger = get_logger(__name__)


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
        
        # Create indexes (idempotent)
        await create_indexes()
        
        logger.info("Application startup complete")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await db_manager.disconnect()
    logger.info("Application shutdown complete")


async def create_indexes():
    """Create MongoDB indexes for optimal query performance."""
    db = db_manager.db
    
    # Users collection indexes
    await db.users.create_index("id", unique=True)
    await db.users.create_index("phone", unique=True)
    await db.users.create_index("referral_code", unique=True)
    
    # Matches collection indexes
    await db.matches.create_index("id", unique=True)
    await db.matches.create_index("external_match_id", sparse=True)
    await db.matches.create_index("status")
    await db.matches.create_index("start_time")
    await db.matches.create_index([("status", 1), ("start_time", 1)])
    
    # Contests collection indexes
    await db.contests.create_index("id", unique=True)
    await db.contests.create_index("match_id")
    await db.contests.create_index("status")
    await db.contests.create_index([("match_id", 1), ("status", 1)])
    
    # Contest entries collection indexes
    await db.contest_entries.create_index("id", unique=True)
    await db.contest_entries.create_index([("contest_id", 1), ("user_id", 1)], unique=True)
    await db.contest_entries.create_index("user_id")
    await db.contest_entries.create_index("contest_id")
    
    # Questions collection indexes
    await db.questions.create_index("id", unique=True)
    await db.questions.create_index("category")
    await db.questions.create_index("is_active")
    
    # Templates collection indexes
    await db.templates.create_index("id", unique=True)
    await db.templates.create_index("match_type")
    await db.templates.create_index("is_active")
    
    # Question results collection indexes
    await db.question_results.create_index("id", unique=True)
    await db.question_results.create_index([("match_id", 1), ("question_id", 1)], unique=True)
    
    # Wallet transactions collection indexes
    await db.wallet_transactions.create_index("id", unique=True)
    await db.wallet_transactions.create_index("user_id")
    await db.wallet_transactions.create_index([("user_id", 1), ("created_at", -1)])
    
    logger.info("Database indexes created/verified")


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


# Include routers with /api prefix
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")


# Root endpoint
@app.get("/api")
async def root():
    """API root endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs" if settings.DEBUG else "disabled"
    }


# Backwards compatibility endpoint
@app.get("/api/")
async def root_slash():
    """API root endpoint with trailing slash."""
    return await root()
