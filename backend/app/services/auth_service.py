# backend/app/services/auth_service.py

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import Token, UserLogin, UserRegister


class EmailAlreadyExistsError(Exception):
    """
    Raised when attempting to register a user with an email that is
    already in use.

    This is a service-level exception only. The API layer is responsible
    for translating this into an appropriate HTTP response.
    """

    pass


class AuthService:
    """
    Authentication and user-account service.

    Handles user lookup, registration, authentication, and JWT
    token creation.

    The database session is always provided by the caller. This
    service does not create or close database sessions and does not
    contain HTTP-specific logic.
    """

    def get_user_by_email(
        self,
        db: Session,
        email: str,
    ) -> User | None:
        """
        Find a user by email.

        Returns:
            User if found, otherwise None.
        """
        return db.scalar(
            select(User).where(User.email == email)
        )

    def register_user(
        self,
        db: Session,
        user_data: UserRegister,
    ) -> User:
        """
        Register a new user.

        Raises:
            EmailAlreadyExistsError:
                If the email is already registered.
        """

        existing_user = self.get_user_by_email(
            db,
            user_data.email,
        )

        if existing_user is not None:
            raise EmailAlreadyExistsError(
                "A user with this email already exists."
            )

        new_user = User(
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            full_name=user_data.full_name,
        )

        db.add(new_user)

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(new_user)

        return new_user

    def authenticate_user(
        self,
        db: Session,
        user_data: UserLogin,
    ) -> User | None:
        """
        Authenticate a user using email and password.

        Returns:
            Authenticated User on success.

            None if:
            - the email does not exist
            - the password is incorrect
            - the account is inactive
        """

        user = self.get_user_by_email(
            db,
            user_data.email,
        )

        if user is None:
            return None

        if not verify_password(
            user_data.password,
            user.password_hash,
        ):
            return None

        if not user.is_active:
            return None

        return user

    def create_user_token(
        self,
        user: User,
    ) -> Token:
        """
        Create a JWT access token for an authenticated user.

        The user's database ID is stored in the JWT "sub" claim
        as a string.
        """

        access_token = create_access_token(
            {
                "sub": str(user.id),
            }
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
        )