"""
Security utilities for authentication.

Provides password hashing, JWT token creation and validation.
"""

import hashlib
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain text password.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: Plain text password to check
        hashed_password: Stored hash to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload data (typically contains 'sub' with user_id)
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    return encoded_jwt


def password_reset_fingerprint(hashed_password: str) -> str:
    """
    Short fingerprint of the user's current password hash.

    Embedding this in the reset token makes the token single-use: once the
    password changes, the fingerprint no longer matches and any previously
    issued reset link stops working.
    """
    return hashlib.sha256((hashed_password or "").encode()).hexdigest()[:16]


def create_password_reset_token(user_id: int, hashed_password: str) -> str:
    """
    Create a short-lived JWT for resetting a password.

    The token carries a dedicated "type" claim so it cannot be used as an
    access token, a "pwh" fingerprint of the current password (single-use),
    and expires after PASSWORD_RESET_EXPIRE_MINUTES.
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(user_id),
        "type": "password_reset",
        "pwh": password_reset_fingerprint(hashed_password),
        "exp": expire,
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_password_reset_token(token: str, hashed_password: str) -> Optional[int]:
    """
    Validate a password reset token against the user's current password hash.

    Returns the user id if the token is valid, of type "password_reset", not
    expired, and still bound to the current password; otherwise None.
    """
    payload = decode_token(token)
    if not payload or payload.get("type") != "password_reset":
        return None
    if payload.get("pwh") != password_reset_fingerprint(hashed_password):
        return None
    sub = payload.get("sub")
    if sub is None:
        return None
    try:
        return int(sub)
    except (TypeError, ValueError):
        return None


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload dict, or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
