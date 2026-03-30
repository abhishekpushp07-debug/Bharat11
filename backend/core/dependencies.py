"""
FastAPI Dependencies
Dependency injection for authentication, database, and rate limiting.
"""
from typing import Optional, Annotated

from fastapi import Depends, Header, HTTPException, Request
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
        
        # Check if token was issued before PIN change (token invalidation)
        pin_changed_at = user_doc.get("pin_changed_at")
        token_iat = payload.get("iat")
        if pin_changed_at and token_iat:
            from datetime import datetime, timezone
            if isinstance(pin_changed_at, str):
                pca = datetime.fromisoformat(pin_changed_at.replace('Z', '+00:00'))
            else:
                pca = pin_changed_at
            token_issued = datetime.fromtimestamp(token_iat, tz=timezone.utc)
            if token_issued < pca:
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


# In-memory rate limit fallback with automatic cleanup
import time as _time
import threading as _threading

_rate_limit_store: dict = {}  # {identifier: [timestamps]}
_rate_limit_lock = _threading.Lock()
_last_cleanup = 0.0
_CLEANUP_INTERVAL = 300  # Cleanup every 5 minutes

def _cleanup_rate_limit_store(now: float, window_seconds: int) -> None:
    """Remove stale entries older than window to prevent memory leak."""
    global _last_cleanup
    if now - _last_cleanup < _CLEANUP_INTERVAL:
        return
    _last_cleanup = now
    cutoff = now - window_seconds
    stale_keys = [k for k, v in _rate_limit_store.items() if not v or v[-1] < cutoff]
    for k in stale_keys:
        del _rate_limit_store[k]

def _memory_rate_limit(identifier: str, max_requests: int, window_seconds: int) -> tuple:
    """In-memory rate limiting fallback with periodic cleanup."""
    now = _time.time()
    cutoff = now - window_seconds
    
    with _rate_limit_lock:
        _cleanup_rate_limit_store(now, window_seconds)
        
        if identifier not in _rate_limit_store:
            _rate_limit_store[identifier] = []
        
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


async def require_admin(current_user: CurrentUser) -> User:
    """
    Admin role guard. Raises 403 if user is not admin.
    For now: first registered user (phone 9876543210) is auto-admin.
    Future: proper role management.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user

AdminUser = Annotated[User, Depends(require_admin)]
