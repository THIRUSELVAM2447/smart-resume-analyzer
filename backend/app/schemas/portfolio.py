from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PortfolioGenerate(BaseModel):
    """Generate or refresh a portfolio from an owned parsed resume version."""

    resume_version_id: int = Field(gt=0)


class PortfolioUpdate(BaseModel):
    """User-editable presentation fields for an existing portfolio."""

    headline: str | None = Field(default=None, max_length=255)
    bio: str | None = None
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    location: str | None = Field(default=None, max_length=255)
    linkedin_url: str | None = Field(default=None, max_length=500)
    github_url: str | None = Field(default=None, max_length=500)
    skills: list[str] | None = None
    projects: list[str] | None = None
    is_published: bool | None = None


class PortfolioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    headline: str | None
    bio: str | None
    email: str | None
    phone: str | None
    location: str | None
    linkedin_url: str | None
    github_url: str | None
    skills: list | None
    experience: list | None
    education: list | None
    projects: list | None
    certifications: list | None
    achievements: list | None
    theme: str
    is_published: bool
    created_at: datetime
    updated_at: datetime


class PublicPortfolioResponse(PortfolioResponse):
    """Published portfolio response. Deliberately excludes account ownership."""

    pass
