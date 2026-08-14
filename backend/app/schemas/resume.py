# backend/app/schemas/resume.py

from datetime import datetime
from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing_extensions import TypeAliasType


# Named recursive type alias for arbitrary JSON-compatible data.
#
# This supports:
# - dictionaries with JSONValue values
# - lists containing JSONValue values
# - strings
# - integers
# - floats
# - booleans
# - None
#
# TypeAliasType is important here because Pydantic needs a named
# recursive type instead of an implicit recursive Union.
JSONValue = TypeAliasType(
    "JSONValue",
    dict[str, "JSONValue"]
    | list["JSONValue"]
    | str
    | int
    | float
    | bool
    | None,
)


class ResumeBase(BaseModel):
    """
    Reusable input schema for resume metadata.

    The actual uploaded PDF is handled separately by FastAPI's
    UploadFile. This schema only represents resume metadata.
    """

    original_filename: str = Field(max_length=255)

    @field_validator("original_filename")
    @classmethod
    def strip_and_require_filename(cls, value: str) -> str:
        stripped = value.strip()

        if not stripped:
            raise ValueError("original_filename must not be empty")

        return stripped


class ResumeResponse(BaseModel):
    """
    Lightweight response representing a stored Resume.

    Internal fields such as user_id and file_path are intentionally
    excluded from the API response.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ResumeVersionResponse(BaseModel):
    """
    Complete response representing one parsed ResumeVersion.

    The structured resume sections remain flexible JSON because their
    exact structure is determined by the resume parser and may evolve.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    version_number: int
    raw_text: str

    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    summary: str | None = None

    skills: JSONValue | None = None
    experience: JSONValue | None = None
    education: JSONValue | None = None
    projects: JSONValue | None = None
    certifications: JSONValue | None = None
    achievements: JSONValue | None = None

    created_at: datetime


class ResumeDetailResponse(BaseModel):
    """
    Detailed Resume response including its complete version history.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    versions: list[ResumeVersionResponse]