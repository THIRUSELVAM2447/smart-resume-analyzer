from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Portfolio(Base):
    """
    Represents the current approved portfolio state of a user.

    A user can have only one portfolio. Historical portfolio states
    are stored separately in PortfolioVersion records.
    """

    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True,
    )

    slug: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
    )

    headline: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    bio: Mapped[str | None] = mapped_column(
        Text,
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

    skills: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    experience: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    education: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    projects: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    certifications: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    achievements: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    theme: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="default",
        server_default="default",
    )

    is_published: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
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
        back_populates="portfolio",
    )

    versions: Mapped[list["PortfolioVersion"]] = relationship(
        "PortfolioVersion",
        back_populates="portfolio",
        cascade="all, delete-orphan",
    )

    sync_events: Mapped[list["SyncEvent"]] = relationship(
    "SyncEvent",
    back_populates="portfolio",
)


class PortfolioVersion(Base):
    """
    Represents an immutable historical snapshot of a portfolio.

    Every approved portfolio change creates a new version.
    Previous versions are preserved and never overwritten.
    """

    __tablename__ = "portfolio_versions"

    __table_args__ = (
        UniqueConstraint(
            "portfolio_id",
            "version_number",
            name="uq_portfolio_version",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("portfolios.id"),
        nullable=False,
        index=True,
    )

    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    source_resume_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("resume_versions.id"),
        nullable=True,
        index=True,
    )

    snapshot: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    change_summary: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio",
        back_populates="versions",
    )

    source_resume_version: Mapped["ResumeVersion | None"] = relationship(
        "ResumeVersion",
        back_populates="portfolio_versions",
    )

    sync_events: Mapped[list["SyncEvent"]] = relationship(
    "SyncEvent",
    back_populates="portfolio_version",
)