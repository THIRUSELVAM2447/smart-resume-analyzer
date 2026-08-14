# backend/app/database/base.py

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Shared SQLAlchemy declarative base.

    Every ORM model in ResumeIQ (User, Resume, ResumeVersion, Job,
    JobAnalysis, Portfolio, PortfolioVersion, SyncEvent, ...) must
    inherit from this same Base so they are all registered in one
    shared metadata registry.
    """
    pass