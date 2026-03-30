"""
Authentication Service
Handles user registration, login, and token management.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
import re
import random
import string

from motor.motor_asyncio import AsyncIOMotorDatabase

from models.schemas import (
    User, UserCreate, UserLogin, UserResponse, 
    TokenResponse, AuthResponse, UserRank,
    WalletTransaction, TransactionType, TransactionReason,
    generate_unique_referral_code
)
from repositories.user_repository import UserRepository
from repositories.wallet_repository import WalletTransactionRepository
from core.security import password_hasher, jwt_manager
from core.exceptions import (
    InvalidCredentialsError, UserAlreadyExistsError, UserNotFoundError,
    AccountLockedError, InvalidPINError, InvalidPhoneError, InvalidReferralCodeError
)
from config.settings import settings


class AuthService:
    """
    Authentication service handling registration, login, and tokens.
    """
    
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_MINUTES = 15
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.user_repo = UserRepository(db)
        self.wallet_repo = WalletTransactionRepository(db)
    
    def _validate_phone(self, phone: str) -> str:
        """
        Validate and clean phone number.
        Indian mobile: 10 digits starting with 6-9.
        """
        import re
        # Remove all non-digits
        cleaned = ''.join(c for c in phone if c.isdigit())
        
        # Handle country code prefix (+91, 91, 0)
        if len(cleaned) > 10:
            cleaned = cleaned[-10:]
        
        # Must be exactly 10 digits
        if len(cleaned) != 10:
            raise InvalidPhoneError()
        
        # Indian mobile numbers start with 6, 7, 8, or 9
        if not re.match(r'^[6-9]\d{9}$', cleaned):
            raise InvalidPhoneError()
        
        return cleaned
    
    def _validate_pin(self, pin: str) -> str:
        """Validate PIN format."""
        if not pin or len(pin) != 4 or not pin.isdigit():
            raise InvalidPINError()
        return pin
    
    def _generate_username(self, phone: str) -> str:
        """Generate a default username from phone."""
        suffix = ''.join(random.choices(string.digits, k=4))
        return f"Player{phone[-4:]}{suffix}"
    
    def _user_to_response(self, user: User) -> UserResponse:
        """Convert User model to response DTO."""
        return UserResponse(
            id=user.id,
            phone=user.phone,
            username=user.username,
            avatar_url=user.avatar_url,
            coins_balance=user.coins_balance,
            rank_title=user.rank_title,
            total_points=user.total_points,
            matches_played=user.matches_played,
            contests_won=user.contests_won,
            referral_code=user.referral_code,
            daily_streak=user.daily_streak,
            is_admin=user.is_admin,
            created_at=user.created_at
        )
    
    def _create_tokens(self, user: User) -> TokenResponse:
        """Create access and refresh tokens for user."""
        access_token = jwt_manager.create_access_token(
            user_id=user.id,
            phone=user.phone
        )
        refresh_token = jwt_manager.create_refresh_token(user.id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=jwt_manager.get_token_expiry_seconds()
        )
    
    async def register(
        self,
        phone: str,
        pin: str,
        username: Optional[str] = None,
        referral_code: Optional[str] = None
    ) -> AuthResponse:
        """
        Register a new user.
        
        Args:
            phone: Phone number (10 digits)
            pin: 4-digit PIN
            username: Optional custom username
            referral_code: Optional referral code from another user
        
        Returns:
            AuthResponse with tokens and user data
        
        Raises:
            InvalidPhoneError: Invalid phone format
            InvalidPINError: Invalid PIN format
            UserAlreadyExistsError: Phone already registered
            InvalidReferralCodeError: Invalid referral code
        """
        # Validate inputs
        cleaned_phone = self._validate_phone(phone)
        validated_pin = self._validate_pin(pin)
        
        # Check if phone already exists
        if await self.user_repo.phone_exists(cleaned_phone):
            raise UserAlreadyExistsError(cleaned_phone)
        
        # Validate referral code if provided
        referrer_id = None
        if referral_code:
            referrer = await self.user_repo.find_by_referral_code(referral_code.upper())
            if not referrer:
                raise InvalidReferralCodeError()
            referrer_id = referrer.id
        
        # Create user
        user = User(
            phone=cleaned_phone,
            pin_hash=password_hasher.hash(validated_pin),
            username=username or self._generate_username(cleaned_phone),
            coins_balance=settings.SIGNUP_BONUS_COINS,
            referred_by=referrer_id
        )
        
        # Generate collision-safe referral code
        unique_code = await generate_unique_referral_code(self.db)
        user.referral_code = unique_code
        
        # Save user
        await self.user_repo.create(user)
        
        # Create signup bonus transaction
        await self.wallet_repo.create_transaction(
            user_id=user.id,
            amount=settings.SIGNUP_BONUS_COINS,
            transaction_type=TransactionType.CREDIT,
            reason=TransactionReason.SIGNUP_BONUS,
            balance_after=settings.SIGNUP_BONUS_COINS,
            description=f"Welcome bonus! You received {settings.SIGNUP_BONUS_COINS} coins"
        )
        
        # If referred, give bonus to referrer
        if referrer_id:
            referral_bonus = 1000  # Referral bonus amount
            referrer = await self.user_repo.find_by_id(referrer_id)
            if referrer:
                new_balance = referrer.coins_balance + referral_bonus
                await self.user_repo.update_coins(referrer_id, referral_bonus, "add")
                await self.wallet_repo.create_transaction(
                    user_id=referrer_id,
                    amount=referral_bonus,
                    transaction_type=TransactionType.CREDIT,
                    reason=TransactionReason.REFERRAL_BONUS,
                    balance_after=new_balance,
                    reference_id=user.id,
                    description=f"Referral bonus for inviting {user.username}"
                )
        
        # Create tokens
        tokens = self._create_tokens(user)
        user_response = self._user_to_response(user)
        
        return AuthResponse(token=tokens, user=user_response)
    
    async def login(self, phone: str, pin: str) -> AuthResponse:
        """
        Login user with phone and PIN.
        
        Args:
            phone: Phone number
            pin: 4-digit PIN
        
        Returns:
            AuthResponse with tokens and user data
        
        Raises:
            InvalidCredentialsError: Wrong phone or PIN
            AccountLockedError: Too many failed attempts
        """
        # Validate inputs
        cleaned_phone = self._validate_phone(phone)
        validated_pin = self._validate_pin(pin)
        
        # Find user
        user = await self.user_repo.find_by_phone(cleaned_phone)
        if not user:
            raise InvalidCredentialsError()
        
        # Check if account is locked
        if user.locked_until:
            lock_time = user.locked_until
            if isinstance(lock_time, str):
                lock_time = datetime.fromisoformat(lock_time.replace('Z', '+00:00'))
            
            if datetime.now(timezone.utc) < lock_time:
                remaining = (lock_time - datetime.now(timezone.utc)).total_seconds() / 60
                raise AccountLockedError(int(remaining) + 1)
            else:
                # Lockout expired - auto-reset failed attempts
                await self.user_repo.reset_failed_login(user.id)
        
        # Check if banned
        if user.is_banned:
            raise InvalidCredentialsError("Account has been suspended")
        
        # Verify PIN
        if not password_hasher.verify(validated_pin, user.pin_hash):
            # Increment failed attempts
            attempts = await self.user_repo.increment_failed_login(user.id)
            
            if attempts >= self.MAX_LOGIN_ATTEMPTS:
                # Lock account
                lock_until = datetime.now(timezone.utc) + timedelta(minutes=self.LOCKOUT_MINUTES)
                await self.user_repo.lock_account(user.id, lock_until)
                raise AccountLockedError(self.LOCKOUT_MINUTES)
            
            raise InvalidCredentialsError()
        
        # Reset failed attempts on successful login
        await self.user_repo.reset_failed_login(user.id)
        
        # Create tokens
        tokens = self._create_tokens(user)
        user_response = self._user_to_response(user)
        
        return AuthResponse(token=tokens, user=user_response)
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh access token using refresh token.
        Validates pin_changed_at for token revocation.
        Returns rotated tokens (new refresh token too).
        """
        payload = jwt_manager.decode_token(refresh_token)
        
        if payload.get("type") != "refresh":
            from core.exceptions import InvalidTokenError
            raise InvalidTokenError()
        
        user_id = payload.get("sub")
        user = await self.user_repo.find_by_id(user_id)
        
        if not user:
            raise UserNotFoundError()
        
        if user.is_banned:
            from core.exceptions import InvalidTokenError
            raise InvalidTokenError()
        
        # Check if token was issued before PIN change
        pin_changed_at = getattr(user, 'pin_changed_at', None)
        if pin_changed_at is None:
            # Check raw doc
            raw = await self.db.users.find_one({"id": user_id}, {"_id": 0, "pin_changed_at": 1})
            pin_changed_at = raw.get("pin_changed_at") if raw else None
        
        if pin_changed_at and payload.get("iat"):
            if isinstance(pin_changed_at, str):
                pca = datetime.fromisoformat(pin_changed_at.replace('Z', '+00:00'))
            else:
                pca = pin_changed_at
            token_issued = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
            if token_issued < pca:
                from core.exceptions import InvalidTokenError
                raise InvalidTokenError()
        
        # Rotate: issue both new access AND new refresh
        return self._create_tokens(user)
    
    async def get_current_user(self, user_id: str) -> UserResponse:
        """Get current user by ID."""
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return self._user_to_response(user)
    
    async def change_pin(
        self,
        user_id: str,
        old_pin: str,
        new_pin: str
    ) -> bool:
        """
        Change user's PIN and invalidate old tokens via pin_changed_at.
        """
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        
        self._validate_pin(old_pin)
        self._validate_pin(new_pin)
        
        if not password_hasher.verify(old_pin, user.pin_hash):
            raise InvalidCredentialsError("Current PIN is incorrect")
        
        new_hash = password_hasher.hash(new_pin)
        now = datetime.now(timezone.utc).isoformat()
        return await self.user_repo.update_by_id(
            user_id,
            {"$set": {"pin_hash": new_hash, "pin_changed_at": now, "updated_at": now}}
        )

    async def generate_new_tokens(self, user_id: str, phone: str) -> dict:
        """Generate new access+refresh tokens for a user after PIN change."""
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        tokens = self._create_tokens(user)
        return {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token
        }
