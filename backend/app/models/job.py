from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Job(Base):
    """
    Represents a job posting saved or analyzed by a user.

    A Job stores the normalized job posting itself. Analysis results
    belong to the JobAnalysis model.
    """

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    company_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    source_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
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
        back_populates="jobs",
    )

    analyses: Mapped[list["JobAnalysis"]] = relationship(
        "JobAnalysis",
        back_populates="job",
        cascade="all, delete-orphan",
    )