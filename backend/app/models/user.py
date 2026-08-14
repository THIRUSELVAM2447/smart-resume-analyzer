from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class User(Base):
    """
    ORM model representing a ResumeIQ user account.

    Stores account identity and authentication information.
    Password hashing and authentication logic are handled
    by the application layer.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
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

    resumes: Mapped[list["Resume"]] = relationship(
        "Resume",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    jobs: Mapped[list["Job"]] = relationship(
    "Job",
    back_populates="user",
    cascade="all, delete-orphan",
    )

    portfolio: Mapped["Portfolio | None"] = relationship(
        "Portfolio",
        back_populates="user",
        uselist=False,
    )

    sync_events: Mapped[list["SyncEvent"]] = relationship(
        "SyncEvent",
        back_populates="user",
    )