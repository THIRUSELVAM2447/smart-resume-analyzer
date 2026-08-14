from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.connection import get_db
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/auth/login",
)


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Authenticate a request using a JWT bearer token and return
    the corresponding database-backed User ORM object.
    """
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise credentials_exception from None

    sub = payload.get("sub")

    if sub is None:
        raise credentials_exception from None

    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise credentials_exception from None

    user = db.scalar(
        select(User).where(User.id == user_id)
    )

    if user is None:
        raise credentials_exception from None

    return user