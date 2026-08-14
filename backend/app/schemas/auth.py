# backend/app/schemas/auth.py

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    """
    Request body for POST /auth/register.

    Represents raw registration input. Password hashing happens later,
    in the service/security layer — never here.
    """

    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)

    @field_validator("full_name")
    @classmethod
    def strip_and_require_full_name(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("full_name must not be empty")
        return stripped


class UserLogin(BaseModel):
    """
    Request body for POST /auth/login.

    Password verification happens later, in the service/security
    layer — never here.
    """

    email: EmailStr
    password: str = Field(min_length=1)


class Token(BaseModel):
    """
    Response body for a successful login: the issued JWT and its type.

    Token generation itself happens in app.core.security — this schema
    only shapes the response.
    """

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """
    Response body representing an authenticated user's public profile.

    Deliberately excludes password and password_hash — the API must
    never expose either. Configured for construction directly from a
    SQLAlchemy User ORM instance (Pydantic v2 "from attributes" mode).
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime