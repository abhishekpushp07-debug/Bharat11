"""
Security Utilities
Password hashing, JWT token management, and security helpers.
"""
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

import bcrypt
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError as JWTInvalidTokenError

from config.settings import settings
from core.exceptions import TokenExpiredError, InvalidTokenError


class PasswordHasher:
    """
    Secure password hashing using bcrypt.
    """
    
    @staticmethod
    def hash(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify(password: str, hashed: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password
            hashed: Hashed password
        
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                hashed.encode('utf-8')
            )
        except Exception:
            return False


class JWTManager:
    """
    JWT token creation and validation.
    """
    
    @staticmethod
    def create_access_token(
        user_id: str,
        phone: str,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new access token.
        
        Args:
            user_id: User's unique ID
            phone: User's phone number
            additional_claims: Extra claims to include
        
        Returns:
            Encoded JWT token
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "sub": user_id,
            "phone": phone,
            "type": "access",
            "iat": now,
            "exp": expire,
            "jti": secrets.token_hex(16)  # Unique token ID
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
    
    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """
        Create a new refresh token.
        
        Args:
            user_id: User's unique ID
        
        Returns:
            Encoded refresh token
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        
        payload = {
            "sub": user_id,
            "type": "refresh",
            "iat": now,
            "exp": expire,
            "jti": secrets.token_hex(16)
        }
        
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Decode and validate a JWT token.
        
        Args:
            token: Encoded JWT token
        
        Returns:
            Decoded payload
        
        Raises:
            TokenExpiredError: If token has expired
            InvalidTokenError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except ExpiredSignatureError:
            raise TokenExpiredError()
        except JWTInvalidTokenError:
            raise InvalidTokenError()
    
    @staticmethod
    def get_token_expiry_seconds() -> int:
        """Get access token expiry time in seconds."""
        return settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60


# Singleton instances
password_hasher = PasswordHasher()
jwt_manager = JWTManager()
