# backend/app/schemas/job.py

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class JobCreate(BaseModel):
    """
    Input schema for creating a job posting.
    """

    title: str | None = Field(default=None, max_length=255)
    company_name: str | None = Field(default=None, max_length=255)
    source_url: str | None = Field(default=None, max_length=1000)
    description: str = Field(min_length=1)
    source_type: str = Field(default="manual", max_length=30)

    @field_validator("title", "company_name", "source_url", "source_type")
    @classmethod
    def strip_optional_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None

        stripped = value.strip()

        if not stripped:
            return None

        return stripped

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Job description must not be empty.")

        return value


class JobUpdate(BaseModel):
    """
    Input schema for updating an existing job posting.

    All fields are optional so callers can update only the
    information they need to change.
    """

    title: str | None = Field(default=None, max_length=255)
    company_name: str | None = Field(default=None, max_length=255)
    source_url: str | None = Field(default=None, max_length=1000)
    description: str | None = None
    source_type: str | None = Field(default=None, max_length=30)

    @field_validator("title", "company_name", "source_url", "source_type")
    @classmethod
    def strip_optional_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None

        stripped = value.strip()

        if not stripped:
            return None

        return stripped

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Job description must not be empty.")

        return value


class JobResponse(BaseModel):
    """
    API response representing a stored job.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str | None
    company_name: str | None
    source_url: str | None
    description: str
    source_type: str
    created_at: datetime
    updated_at: datetime