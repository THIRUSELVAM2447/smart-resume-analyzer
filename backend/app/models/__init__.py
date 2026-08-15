"""
ResumeIQ SQLAlchemy model registry.

Importing this package loads every model module so SQLAlchemy can
resolve all string-based relationship targets before mapper
configuration occurs.
"""

from app.models.user import User
from app.models.resume import Resume, ResumeVersion
from app.models.job import Job
from app.models.job_analysis import JobAnalysis
from app.models.portfolio import Portfolio, PortfolioVersion
from app.models.sync_event import SyncEvent

__all__ = [
    "User",
    "Resume",
    "ResumeVersion",
    "Job",
    "JobAnalysis",
    "Portfolio",
    "PortfolioVersion",
    "SyncEvent",
]