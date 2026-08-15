from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.connection import get_db
from app.models.user import User


# HTTPBearer tells Swagger UI to use the standard
# Authorization: Bearer <token> header.
#
# auto_error=False lets get_current_user() use the same generic
# 401 response for missing and invalid credentials.
bearer_scheme = HTTPBearer(auto_error=False)


# A single, reusable 401 response. Kept generic so it never reveals
# whether the failure was caused by a missing token, invalid token,
# expired token, invalid "sub", or nonexistent user.
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Authenticate a request using a JWT bearer token and return the
    corresponding database-backed User ORM object.

    Raises:
        HTTPException(401): if credentials are missing, the token is
        invalid or expired, the "sub" claim is missing or invalid, or
        no matching user exists.
    """

    if credentials is None:
        raise credentials_exception

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
    except JWTError:
        raise credentials_exception

    sub = payload.get("sub")
    if sub is None:
        raise credentials_exception

    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise credentials_exception

    user = db.scalar(
        select(User).where(User.id == user_id)
    )

    if user is None:
        raise credentials_exception

    return user