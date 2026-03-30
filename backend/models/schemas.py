"""
Pydantic Models for CrickPredict
Canonical data models - Single Source of Truth
All models use strict validation and proper serialization.
"""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
import uuid
import random
import string

from pydantic import BaseModel, Field, field_validator, ConfigDict


# ==================== ENUMS ====================

class UserRank(str, Enum):
    """User rank titles based on total points."""
    ROOKIE = "Rookie"
    PRO = "Pro"
    EXPERT = "Expert"
    LEGEND = "Legend"
    GOAT = "GOAT"


class MatchStatus(str, Enum):
    """Match lifecycle status."""
    UPCOMING = "upcoming"
    LIVE = "live"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    CANCELLED = "cancelled"


class MatchType(str, Enum):
    """Cricket match format."""
    T20 = "T20"
    ODI = "ODI"
    TEST = "Test"


class ContestStatus(str, Enum):
    """Contest lifecycle status."""
    OPEN = "open"
    LOCKED = "locked"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class QuestionCategory(str, Enum):
    """Question categories."""
    BATTING = "batting"
    BOWLING = "bowling"
    POWERPLAY = "powerplay"
    DEATH_OVERS = "death_overs"
    MATCH = "match"
    PLAYER_PERFORMANCE = "player_performance"
    SPECIAL = "special"


class TemplateType(str, Enum):
    """Template types for match phases."""
    FULL_MATCH = "full_match"
    IN_MATCH = "in_match"


class QuestionDifficulty(str, Enum):
    """Question difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class EvaluationType(str, Enum):
    """Types of question evaluation."""
    EXACT_MATCH = "exact_match"
    RANGE_MATCH = "range_match"
    BOOLEAN_MATCH = "boolean_match"
    COMPOUND_MATCH = "compound_match"
    DUAL_RANGE_MATCH = "dual_range_match"


class TransactionType(str, Enum):
    """Wallet transaction types."""
    CREDIT = "credit"
    DEBIT = "debit"


class TransactionReason(str, Enum):
    """Reasons for wallet transactions."""
    SIGNUP_BONUS = "signup_bonus"
    DAILY_REWARD = "daily_reward"
    CONTEST_ENTRY = "contest_entry"
    CONTEST_WIN = "contest_win"
    REFERRAL_BONUS = "referral_bonus"
    ADMIN_CREDIT = "admin_credit"
    ADMIN_DEBIT = "admin_debit"
    REFUND = "refund"


# ==================== HELPER FUNCTIONS ====================

def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def generate_referral_code() -> str:
    """Generate a unique referral code (6 alphanumeric chars). Collision-resistant."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


async def generate_unique_referral_code(db) -> str:
    """Generate referral code with DB uniqueness check (max 5 retries)."""
    for _ in range(5):
        code = generate_referral_code()
        existing = await db.users.find_one({"referral_code": code}, {"_id": 0, "id": 1})
        if not existing:
            return code
    # Fallback: longer code
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


# ==================== BASE MODELS ====================

class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at fields."""
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


# ==================== USER MODELS ====================

class User(TimestampMixin):
    """User model - canonical representation."""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=generate_id)
    phone: str = Field(..., min_length=10, max_length=15)
    pin_hash: str = Field(..., min_length=1)
    username: str = Field(..., min_length=1, max_length=50)
    avatar_url: Optional[str] = Field(default=None)
    coins_balance: int = Field(default=10000, ge=0)
    rank_title: UserRank = Field(default=UserRank.ROOKIE)
    total_points: int = Field(default=0, ge=0)
    matches_played: int = Field(default=0, ge=0)
    contests_won: int = Field(default=0, ge=0)
    referral_code: str = Field(default_factory=generate_referral_code)
    referred_by: Optional[str] = Field(default=None)
    daily_streak: int = Field(default=0, ge=0)
    last_daily_claim: Optional[datetime] = Field(default=None)
    is_banned: bool = Field(default=False)
    is_admin: bool = Field(default=False)
    failed_login_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = Field(default=None)
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format."""
        # Remove any spaces or dashes
        cleaned = ''.join(c for c in v if c.isdigit())
        if len(cleaned) < 10:
            raise ValueError('Phone number must have at least 10 digits')
        return cleaned
    
    def calculate_rank(self) -> UserRank:
        """Calculate rank based on total points."""
        if self.total_points >= 50000:
            return UserRank.GOAT
        elif self.total_points >= 15000:
            return UserRank.LEGEND
        elif self.total_points >= 5000:
            return UserRank.EXPERT
        elif self.total_points >= 1000:
            return UserRank.PRO
        return UserRank.ROOKIE


class UserCreate(BaseModel):
    """DTO for user registration."""
    phone: str = Field(..., min_length=10, max_length=15)
    pin: str = Field(..., min_length=4, max_length=4)
    username: Optional[str] = Field(default=None, max_length=50)
    referral_code: Optional[str] = Field(default=None, max_length=6)
    
    @field_validator('pin')
    @classmethod
    def validate_pin(cls, v: str) -> str:
        """Validate PIN is 4 digits."""
        if not v.isdigit() or len(v) != 4:
            raise ValueError('PIN must be exactly 4 digits')
        return v


class UserLogin(BaseModel):
    """DTO for user login."""
    phone: str = Field(..., min_length=10, max_length=15)
    pin: str = Field(..., min_length=4, max_length=4)


class UserResponse(BaseModel):
    """DTO for user response (excludes sensitive fields)."""
    model_config = ConfigDict(extra="ignore")
    
    id: str
    phone: str
    username: str
    avatar_url: Optional[str]
    coins_balance: int
    rank_title: UserRank
    total_points: int
    matches_played: int
    contests_won: int
    referral_code: str
    daily_streak: int
    is_admin: bool = False
    created_at: datetime


class UserProfileUpdate(BaseModel):
    """DTO for profile update."""
    username: Optional[str] = Field(default=None, max_length=50)
    avatar_url: Optional[str] = Field(default=None)


# ==================== TEAM MODELS ====================

class Team(BaseModel):
    """Cricket team information."""
    name: str
    short_name: str
    logo_url: Optional[str] = None


# ==================== MATCH MODELS ====================

class Match(TimestampMixin):
    """Cricket match model."""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=generate_id)
    external_match_id: Optional[str] = Field(default=None)  # Cricbuzz ID
    team_a: Team
    team_b: Team
    venue: str
    match_type: MatchType = Field(default=MatchType.T20)
    status: MatchStatus = Field(default=MatchStatus.UPCOMING)
    start_time: datetime
    toss_winner: Optional[str] = Field(default=None)
    toss_decision: Optional[str] = Field(default=None)
    live_score: Optional[Dict[str, Any]] = Field(default=None)
    result: Optional[str] = Field(default=None)
    templates_assigned: List[str] = Field(default_factory=list)


class MatchResponse(BaseModel):
    """DTO for match response."""
    model_config = ConfigDict(extra="ignore")
    
    id: str
    team_a: Team
    team_b: Team
    venue: str
    match_type: MatchType
    status: MatchStatus
    start_time: datetime
    toss_winner: Optional[str]
    toss_decision: Optional[str]
    live_score: Optional[Dict[str, Any]]
    result: Optional[str]


# ==================== QUESTION MODELS ====================

class QuestionOption(BaseModel):
    """Single question option."""
    key: str = Field(..., pattern="^[A-D]$")
    text_en: str
    text_hi: str
    min_value: Optional[float] = Field(default=None)
    max_value: Optional[float] = Field(default=None)


class EvaluationRules(BaseModel):
    """Rules for evaluating question answers."""
    type: EvaluationType
    metric: str  # e.g., "innings_1_total", "total_wickets"
    comparator: Optional[str] = Field(default=None)  # ">", "<", "=", "between"
    threshold: Optional[float] = Field(default=None)
    threshold_min: Optional[float] = Field(default=None)
    threshold_max: Optional[float] = Field(default=None)
    resolution_trigger: str  # e.g., "innings_end", "match_end", "powerplay_end"
    secondary_metric: Optional[str] = Field(default=None)  # For dual_range_match


class Question(TimestampMixin):
    """Question bank model."""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=generate_id)
    question_text_en: str
    question_text_hi: str
    category: QuestionCategory
    options: List[QuestionOption] = Field(..., min_length=2, max_length=4)
    points: int = Field(default=50, ge=10, le=200)
    multiplier: float = Field(default=1.0, ge=1.0, le=3.0)
    evaluation_rules: EvaluationRules
    difficulty: QuestionDifficulty = Field(default=QuestionDifficulty.MEDIUM)
    is_active: bool = Field(default=True)


# ==================== TEMPLATE MODELS ====================

class Template(TimestampMixin):
    """Question template - group of questions for a match phase."""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=generate_id)
    name: str
    description: Optional[str] = Field(default=None)
    match_type: MatchType = Field(default=MatchType.T20)
    template_type: TemplateType = Field(default=TemplateType.FULL_MATCH)
    question_ids: List[str] = Field(default_factory=list)
    total_points: int = Field(default=0)
    is_active: bool = Field(default=True)
    is_default: bool = Field(default=False)
    # In-match routing fields
    innings_range: List[int] = Field(default_factory=list)  # e.g. [1] or [2] or [1,2]
    over_start: Optional[int] = Field(default=None)  # e.g. 1
    over_end: Optional[int] = Field(default=None)  # e.g. 6
    answer_deadline_over: Optional[int] = Field(default=None)  # last over to submit answers
    phase_label: Optional[str] = Field(default=None)  # "Innings 1 Powerplay", etc.


# ==================== CONTEST MODELS ====================

class PrizeDistribution(BaseModel):
    """Prize distribution for a rank range."""
    rank_start: int = Field(..., ge=1)
    rank_end: int = Field(..., ge=1)
    prize: int = Field(..., ge=0)
    
    @field_validator('rank_end')
    @classmethod
    def validate_rank_end(cls, v: int, info) -> int:
        if 'rank_start' in info.data and v < info.data['rank_start']:
            raise ValueError('rank_end must be >= rank_start')
        return v


class Contest(TimestampMixin):
    """Contest model."""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=generate_id)
    match_id: str
    template_id: str
    name: str
    entry_fee: int = Field(default=0, ge=0)
    prize_pool: int = Field(default=0, ge=0)
    prize_distribution: List[PrizeDistribution] = Field(default_factory=list)
    max_participants: int = Field(default=1000, ge=2)
    current_participants: int = Field(default=0, ge=0)
    status: ContestStatus = Field(default=ContestStatus.OPEN)
    lock_time: datetime


class ContestResponse(BaseModel):
    """DTO for contest response."""
    model_config = ConfigDict(extra="ignore")
    
    id: str
    match_id: str
    name: str
    entry_fee: int
    prize_pool: int
    prize_distribution: List[PrizeDistribution]
    max_participants: int
    current_participants: int
    status: ContestStatus
    lock_time: datetime


# ==================== PREDICTION MODELS ====================

class Prediction(BaseModel):
    """Single prediction within a contest entry."""
    question_id: str
    selected_option: str = Field(..., pattern="^[A-D]$")
    is_correct: Optional[bool] = Field(default=None)
    points_earned: int = Field(default=0)


class ContestEntry(TimestampMixin):
    """User's entry in a contest."""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=generate_id)
    contest_id: str
    user_id: str
    team_name: str = Field(..., max_length=50)
    predictions: List[Prediction] = Field(default_factory=list)
    total_points: int = Field(default=0)
    submission_time: Optional[datetime] = Field(default=None)
    final_rank: Optional[int] = Field(default=None)
    prize_won: int = Field(default=0)


# ==================== QUESTION RESULT MODEL ====================

class QuestionResult(TimestampMixin):
    """Stores resolved question results for a match."""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=generate_id)
    match_id: str
    question_id: str
    correct_option: str = Field(..., pattern="^[A-D]$")
    resolution_data: Dict[str, Any] = Field(default_factory=dict)
    resolved_at: datetime = Field(default_factory=utc_now)


# ==================== WALLET MODELS ====================

class WalletTransaction(TimestampMixin):
    """Wallet transaction record."""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=generate_id)
    user_id: str
    type: TransactionType
    amount: int = Field(..., gt=0)
    reason: TransactionReason
    reference_id: Optional[str] = Field(default=None)
    balance_after: int = Field(..., ge=0)
    description: Optional[str] = Field(default=None)


class WalletTransactionResponse(BaseModel):
    """DTO for transaction response."""
    model_config = ConfigDict(extra="ignore")
    
    id: str
    type: TransactionType
    amount: int
    reason: TransactionReason
    balance_after: int
    description: Optional[str]
    created_at: datetime


# ==================== AUTH MODELS ====================

class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthResponse(BaseModel):
    """Authentication response."""
    token: TokenResponse
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


# ==================== LEADERBOARD MODELS ====================

class LeaderboardEntry(BaseModel):
    """Single leaderboard entry."""
    rank: int
    user_id: str
    username: str
    team_name: str
    total_points: int
    avatar_url: Optional[str] = None


class LeaderboardResponse(BaseModel):
    """Leaderboard response."""
    contest_id: str
    total_participants: int
    entries: List[LeaderboardEntry]
    user_rank: Optional[int] = None
    user_points: Optional[int] = None


# ==================== HEALTH CHECK MODELS ====================

class HealthStatus(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, Dict[str, Any]]
