"""
FastAPI Dependencies
Dependency injection for authentication, database, and rate limiting.
"""
from typing import Optional, Annotated

from fastapi import Depends, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.database import db_manager, get_db, get_redis
from core.security import jwt_manager
from core.exceptions import (
    InvalidTokenError, 
    TokenExpiredError, 
    UserNotFoundError,
    RateLimitExceededError
)
from core.redis_manager import RedisManager
from config.settings import settings
from models.schemas import User

import redis.asyncio as aioredis
from motor.motor_asyncio import AsyncIOMotorDatabase


# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


async def get_redis_manager() -> RedisManager:
    """Get Redis manager instance."""
    redis_client = get_redis()
    return RedisManager(redis_client)


async def get_current_user_optional(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
) -> Optional[User]:
    """
    Get current user from JWT token (optional).
    Returns None if no token or invalid token.
    """
    if not credentials:
        return None
    
    try:
        payload = jwt_manager.decode_token(credentials.credentials)
        
        if payload.get("type") != "access":
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Fetch user from database
        user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user_doc:
            return None
        
        return User(**user_doc)
    
    except (TokenExpiredError, InvalidTokenError):
        return None


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
) -> User:
    """
    Get current user from JWT token (required).
    Raises exception if not authenticated.
    """
    if not credentials:
        raise InvalidTokenError()
    
    try:
        payload = jwt_manager.decode_token(credentials.credentials)
        
        if payload.get("type") != "access":
            raise InvalidTokenError()
        
        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError()
        
        # Fetch user from database
        user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user_doc:
            raise UserNotFoundError()
        
        user = User(**user_doc)
        
        # Check if user is banned
        if user.is_banned:
            raise InvalidTokenError()
        
        return user
    
    except (TokenExpiredError, InvalidTokenError) as e:
        raise e.to_http_exception()


async def rate_limit_dependency(
    request: Request,
    redis_manager: Annotated[RedisManager, Depends(get_redis_manager)]
) -> None:
    """
    Rate limiting dependency.
    Uses IP address as identifier.
    Falls back to in-memory tracking when Redis is unavailable.
    Returns rate limit info in response headers.
    """
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    
    identifier = f"ip:{client_ip}"
    max_requests = settings.RATE_LIMIT_REQUESTS
    window = settings.RATE_LIMIT_WINDOW_SECONDS
    
    if redis_manager.is_available:
        is_allowed, remaining = await redis_manager.check_rate_limit(
            identifier, max_requests, window
        )
    else:
        # In-memory fallback (per-process, not shared across workers)
        is_allowed, remaining = _memory_rate_limit(identifier, max_requests, window)
    
    # Store rate limit info for response headers
    request.state.rate_limit_remaining = remaining
    request.state.rate_limit_limit = max_requests
    request.state.rate_limit_window = window
    
    if not is_allowed:
        raise RateLimitExceededError(window).to_http_exception()


# In-memory rate limit fallback (simple, per-process)
import time as _time
_rate_limit_store: dict = {}  # {identifier: [timestamps]}

def _memory_rate_limit(identifier: str, max_requests: int, window_seconds: int) -> tuple:
    """Simple in-memory rate limiting fallback."""
    now = _time.time()
    cutoff = now - window_seconds
    
    # Get or create entry
    if identifier not in _rate_limit_store:
        _rate_limit_store[identifier] = []
    
    # Clean old entries
    _rate_limit_store[identifier] = [
        ts for ts in _rate_limit_store[identifier] if ts > cutoff
    ]
    
    current_count = len(_rate_limit_store[identifier])
    
    if current_count >= max_requests:
        return False, 0
    
    _rate_limit_store[identifier].append(now)
    return True, max_requests - current_count - 1


# Type aliases for cleaner function signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[Optional[User], Depends(get_current_user_optional)]
Database = Annotated[AsyncIOMotorDatabase, Depends(get_db)]
Redis = Annotated[RedisManager, Depends(get_redis_manager)]
RateLimited = Annotated[None, Depends(rate_limit_dependency)]
