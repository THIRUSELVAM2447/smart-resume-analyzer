from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# ---------- Password hashing ----------

# Centralized password hashing configuration.
# bcrypt automatically handles generating and storing a salt
# as part of the resulting password hash.
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """
    Hash a plain-text password before storing it.

    Never store a user's plain-text password in the database.
    """
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Verify a plain-text password against a stored password hash.

    Returns:
        True if the password matches.
        False otherwise.
    """
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# ---------- JWT access tokens ----------


def create_access_token(data: dict[str, Any]) -> str:
    """
    Create a signed JWT access token.

    The supplied claims are copied and an expiration (`exp`)
    claim is added before signing the token.
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode["exp"] = expire

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT access token.

    The JWT library verifies:
    - token signature
    - token expiration
    - token structure

    Raises:
        JWTError: If the token is invalid, malformed,
        expired, or has an invalid signature.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )