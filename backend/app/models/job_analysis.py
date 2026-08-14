from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class JobAnalysis(Base):
    """
    Represents one ATS analysis performed by comparing a Job
    against a specific ResumeVersion.

    The model stores analysis results only. Scoring, NLP,
    grammar checking, and recommendations are handled by
    service-layer components.
    """

    __tablename__ = "job_analyses"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"),
        nullable=False,
        index=True,
    )

    resume_version_id: Mapped[int] = mapped_column(
        ForeignKey("resume_versions.id"),
        nullable=False,
        index=True,
    )

    overall_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    skill_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    matched_skills: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    missing_skills: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    extra_skills: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    grammar_issues: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    recommendations: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    analysis_snapshot: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    job: Mapped["Job"] = relationship(
        "Job",
        back_populates="analyses",
    )

    resume_version: Mapped["ResumeVersion"] = relationship(
        "ResumeVersion",
        back_populates="analyses",
    )