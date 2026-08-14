from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.schemas.auth import Token, UserLogin, UserRegister, UserResponse
from app.services.auth_service import AuthService, EmailAlreadyExistsError


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)

auth_service = AuthService()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
) -> User:
    """Register a new user account."""
    try:
        new_user = auth_service.register_user(db, user_data)
    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    return new_user


@router.post(
    "/login",
    response_model=Token,
)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db),
) -> Token:
    """Authenticate a user and issue an access token."""
    user = auth_service.authenticate_user(db, user_data)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return auth_service.create_user_token(user)


@router.get(
    "/me",
    response_model=UserResponse,
)
def read_current_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Return the currently authenticated user's profile."""
    return current_user