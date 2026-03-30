"""
Authentication Router
Handles authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from core.database import get_db
from core.dependencies import CurrentUser, rate_limit_dependency
from core.exceptions import CrickPredictException
from models.schemas import (
    UserCreate, UserLogin, AuthResponse, TokenResponse,
    RefreshTokenRequest, UserResponse
)
from services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> AuthService:
    """Dependency to get AuthService instance."""
    return AuthService(db)


class ChangePinBody(BaseModel):
    """Request body for PIN change."""
    old_pin: str
    new_pin: str


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register with phone number and 4-digit PIN. Returns tokens and user data.",
    dependencies=[Depends(rate_limit_dependency)]
)
async def register(
    data: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> AuthResponse:
    """
    Register a new user account.
    
    - **phone**: 10-digit phone number
    - **pin**: 4-digit PIN (password)
    - **username**: Optional custom username
    - **referral_code**: Optional referral code for bonus coins
    
    Returns JWT tokens and user profile with 10,000 signup bonus coins.
    """
    try:
        return await auth_service.register(
            phone=data.phone,
            pin=data.pin,
            username=data.username,
            referral_code=data.referral_code
        )
    except CrickPredictException as e:
        raise e.to_http_exception()


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login user",
    description="Login with phone number and PIN. Returns tokens and user data.",
    dependencies=[Depends(rate_limit_dependency)]
)
async def login(
    data: UserLogin,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> AuthResponse:
    """
    Login with phone and PIN.
    
    - **phone**: Registered phone number
    - **pin**: 4-digit PIN
    
    Account locks after 5 failed attempts for 15 minutes.
    """
    try:
        return await auth_service.login(
            phone=data.phone,
            pin=data.pin
        )
    except CrickPredictException as e:
        raise e.to_http_exception()


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get new access token using refresh token."
)
async def refresh_token(
    data: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> TokenResponse:
    """
    Refresh access token using a valid refresh token.
    
    Use this when access token expires to get a new one
    without requiring the user to login again.
    """
    try:
        return await auth_service.refresh_token(data.refresh_token)
    except CrickPredictException as e:
        raise e.to_http_exception()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get profile of currently authenticated user."
)
async def get_me(
    current_user: CurrentUser,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> UserResponse:
    """
    Get the profile of the currently authenticated user.
    
    Requires valid access token in Authorization header.
    """
    try:
        return await auth_service.get_current_user(current_user.id)
    except CrickPredictException as e:
        raise e.to_http_exception()


@router.put(
    "/change-pin",
    summary="Change PIN",
    description="Change user's PIN. Requires current PIN verification. Invalidates all existing tokens.",
    dependencies=[Depends(rate_limit_dependency)]
)
async def change_pin(
    data: ChangePinBody,
    current_user: CurrentUser,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> dict:
    """
    Change the user's PIN.
    
    - **old_pin**: Current 4-digit PIN
    - **new_pin**: New 4-digit PIN
    
    After PIN change, old tokens become invalid (pin_changed_at check).
    Returns success status with new tokens.
    """
    try:
        success = await auth_service.change_pin(
            user_id=current_user.id,
            old_pin=data.old_pin,
            new_pin=data.new_pin
        )
        # Issue new tokens after PIN change (old ones will be invalid)
        new_tokens = await auth_service.generate_new_tokens(current_user.id, current_user.phone)
        return {
            "success": success,
            "message": "PIN changed successfully. Old sessions invalidated.",
            "token": {
                "access_token": new_tokens["access_token"],
                "refresh_token": new_tokens["refresh_token"],
                "token_type": "bearer"
            }
        }
    except CrickPredictException as e:
        raise e.to_http_exception()
