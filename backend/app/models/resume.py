from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Resume(Base):
    """
    Represents a resume document owned by a user.

    A Resume acts as the container for the uploaded file and its
    version history. Parsed resume information is stored in
    ResumeVersion records.
    """

    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="resumes",
    )

    versions: Mapped[list["ResumeVersion"]] = relationship(
        "ResumeVersion",
        back_populates="resume",
        cascade="all, delete-orphan",
    )


class ResumeVersion(Base):
    """
    Represents one parsed snapshot of a resume.

    Every new parsing operation creates a new version instead of
    overwriting the previous version. This allows ResumeIQ to compare
    resume changes over time and support portfolio synchronization.
    """

    __tablename__ = "resume_versions"

    __table_args__ = (
        UniqueConstraint(
            "resume_id",
            "version_number",
            name="uq_resume_version",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id"),
        nullable=False,
        index=True,
    )

    version_number: Mapped[int] = mapped_column(
        nullable=False,
    )

    raw_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    linkedin_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    github_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    skills: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    experience: Mapped[list[dict] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    education: Mapped[list[dict] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    projects: Mapped[list[dict] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    certifications: Mapped[list[dict] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    achievements: Mapped[list[dict] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    resume: Mapped["Resume"] = relationship(
        "Resume",
        back_populates="versions",
    )

    analyses: Mapped[list["JobAnalysis"]] = relationship(
        "JobAnalysis",
        back_populates="resume_version",
        cascade="all, delete-orphan",
    )

    portfolio_versions: Mapped[list["PortfolioVersion"]] = relationship(
        "PortfolioVersion",
        back_populates="source_resume_version",
    )

    sync_events: Mapped[list["SyncEvent"]] = relationship(
        "SyncEvent",
        back_populates="resume_version",
    )