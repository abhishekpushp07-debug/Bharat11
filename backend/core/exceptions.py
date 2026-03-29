"""
Custom Exception Hierarchy for CrickPredict
Centralized error handling with proper HTTP status codes and messages.
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class CrickPredictException(Exception):
    """Base exception for all CrickPredict errors."""
    
    def __init__(
        self, 
        message: str, 
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)
    
    def to_http_exception(self) -> HTTPException:
        """Convert to FastAPI HTTPException."""
        return HTTPException(
            status_code=self.status_code,
            detail={
                "error": self.code,
                "message": self.message,
                "details": self.details
            }
        )


# ==================== Authentication Errors ====================

class AuthenticationError(CrickPredictException):
    """Base class for authentication errors."""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid."""
    
    def __init__(self, message: str = "Invalid phone number or PIN"):
        super().__init__(
            message=message,
            code="INVALID_CREDENTIALS",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class TokenExpiredError(AuthenticationError):
    """Raised when JWT token has expired."""
    
    def __init__(self):
        super().__init__(
            message="Token has expired",
            code="TOKEN_EXPIRED",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class InvalidTokenError(AuthenticationError):
    """Raised when JWT token is invalid."""
    
    def __init__(self):
        super().__init__(
            message="Invalid token",
            code="INVALID_TOKEN",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AccountLockedError(AuthenticationError):
    """Raised when account is locked due to too many failed attempts."""
    
    def __init__(self, unlock_time_minutes: int = 15):
        super().__init__(
            message=f"Account locked. Try again in {unlock_time_minutes} minutes",
            code="ACCOUNT_LOCKED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"unlock_after_minutes": unlock_time_minutes}
        )


# ==================== User Errors ====================

class UserNotFoundError(CrickPredictException):
    """Raised when user is not found."""
    
    def __init__(self, identifier: str = ""):
        super().__init__(
            message="User not found" + (f": {identifier}" if identifier else ""),
            code="USER_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )


class UserAlreadyExistsError(CrickPredictException):
    """Raised when trying to create a user that already exists."""
    
    def __init__(self, phone: str = ""):
        super().__init__(
            message="User with this phone number already exists",
            code="USER_ALREADY_EXISTS",
            status_code=status.HTTP_409_CONFLICT
        )


class InvalidReferralCodeError(CrickPredictException):
    """Raised when referral code is invalid."""
    
    def __init__(self):
        super().__init__(
            message="Invalid referral code",
            code="INVALID_REFERRAL_CODE",
            status_code=status.HTTP_400_BAD_REQUEST
        )


# ==================== Wallet Errors ====================

class InsufficientBalanceError(CrickPredictException):
    """Raised when user doesn't have enough coins."""
    
    def __init__(self, required: int, available: int):
        super().__init__(
            message=f"Insufficient balance. Required: {required}, Available: {available}",
            code="INSUFFICIENT_BALANCE",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"required": required, "available": available}
        )


class DailyRewardAlreadyClaimedError(CrickPredictException):
    """Raised when daily reward was already claimed today."""
    
    def __init__(self):
        super().__init__(
            message="Daily reward already claimed today",
            code="DAILY_REWARD_CLAIMED",
            status_code=status.HTTP_400_BAD_REQUEST
        )


# ==================== Contest Errors ====================

class ContestNotFoundError(CrickPredictException):
    """Raised when contest is not found."""
    
    def __init__(self, contest_id: str = ""):
        super().__init__(
            message="Contest not found" + (f": {contest_id}" if contest_id else ""),
            code="CONTEST_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )


class ContestLockedError(CrickPredictException):
    """Raised when trying to join/modify a locked contest."""
    
    def __init__(self):
        super().__init__(
            message="Contest is locked. No more entries or changes allowed",
            code="CONTEST_LOCKED",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class ContestFullError(CrickPredictException):
    """Raised when contest has reached max participants."""
    
    def __init__(self):
        super().__init__(
            message="Contest is full",
            code="CONTEST_FULL",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class AlreadyJoinedContestError(CrickPredictException):
    """Raised when user has already joined the contest."""
    
    def __init__(self):
        super().__init__(
            message="You have already joined this contest",
            code="ALREADY_JOINED",
            status_code=status.HTTP_400_BAD_REQUEST
        )


# ==================== Match Errors ====================

class MatchNotFoundError(CrickPredictException):
    """Raised when match is not found."""
    
    def __init__(self, match_id: str = ""):
        super().__init__(
            message="Match not found" + (f": {match_id}" if match_id else ""),
            code="MATCH_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )


class MatchNotLiveError(CrickPredictException):
    """Raised when trying to access live data of non-live match."""
    
    def __init__(self):
        super().__init__(
            message="Match is not live",
            code="MATCH_NOT_LIVE",
            status_code=status.HTTP_400_BAD_REQUEST
        )


# ==================== Prediction Errors ====================

class PredictionLockedError(CrickPredictException):
    """Raised when trying to modify locked predictions."""
    
    def __init__(self):
        super().__init__(
            message="Predictions are locked. Cannot modify",
            code="PREDICTIONS_LOCKED",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class IncompletePredictionsError(CrickPredictException):
    """Raised when not all questions are answered."""
    
    def __init__(self, answered: int, required: int):
        super().__init__(
            message=f"Incomplete predictions. Answered: {answered}, Required: {required}",
            code="INCOMPLETE_PREDICTIONS",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"answered": answered, "required": required}
        )


# ==================== Validation Errors ====================

class ValidationError(CrickPredictException):
    """Raised for validation failures."""
    
    def __init__(self, message: str, field: str = ""):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"field": field} if field else {}
        )


class InvalidPINError(ValidationError):
    """Raised when PIN format is invalid."""
    
    def __init__(self):
        super().__init__(
            message="PIN must be exactly 4 digits",
            field="pin"
        )


class InvalidPhoneError(ValidationError):
    """Raised when phone format is invalid."""
    
    def __init__(self):
        super().__init__(
            message="Invalid phone number format. Must be 10 digits",
            field="phone"
        )


# ==================== Rate Limit Errors ====================

class RateLimitExceededError(CrickPredictException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, retry_after_seconds: int = 60):
        super().__init__(
            message=f"Rate limit exceeded. Retry after {retry_after_seconds} seconds",
            code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after_seconds": retry_after_seconds}
        )


# ==================== External Service Errors ====================

class ExternalServiceError(CrickPredictException):
    """Raised when external service (Cricbuzz, etc.) fails."""
    
    def __init__(self, service: str, message: str = "Service unavailable"):
        super().__init__(
            message=f"{service}: {message}",
            code="EXTERNAL_SERVICE_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"service": service}
        )
