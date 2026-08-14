from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class SyncEvent(Base):
    """
    Represents one attempt to synchronize a ResumeVersion
    with a user's current Portfolio.

    A SyncEvent records the proposed changes, the portfolio state
    before the change, the proposed state, and the eventual result.

    Business logic such as diff generation, approval, rejection,
    and applying changes belongs to the service layer.
    """

    __tablename__ = "sync_events"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    resume_version_id: Mapped[int] = mapped_column(
        ForeignKey("resume_versions.id"),
        nullable=False,
        index=True,
    )

    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("portfolios.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="preview",
        server_default="preview",
        index=True,
    )

    changes: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    previous_snapshot: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    proposed_snapshot: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    portfolio_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("portfolio_versions.id"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    applied_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="sync_events",
    )

    resume_version: Mapped["ResumeVersion"] = relationship(
        "ResumeVersion",
        back_populates="sync_events",
    )

    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio",
        back_populates="sync_events",
    )

    portfolio_version: Mapped["PortfolioVersion | None"] = relationship(
        "PortfolioVersion",
        back_populates="sync_events",
    )