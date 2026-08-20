import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio, PortfolioVersion
from app.models.resume import Resume, ResumeVersion
from app.models.user import User
from app.schemas.portfolio import PortfolioUpdate


class PortfolioService:
    """Portfolio generation and ownership-aware retrieval/update operations."""

    def get_user_portfolio(self, db: Session, user: User) -> Portfolio | None:
        return db.scalar(select(Portfolio).where(Portfolio.user_id == user.id))

    def get_portfolio(self, db: Session, user: User, portfolio_id: int) -> Portfolio | None:
        return db.scalar(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == user.id))

    def get_public_portfolio(self, db: Session, slug: str) -> Portfolio | None:
        return db.scalar(select(Portfolio).where(Portfolio.slug == slug, Portfolio.is_published.is_(True)))

    def get_user_resume_version(self, db: Session, user: User, resume_version_id: int) -> ResumeVersion | None:
        return db.scalar(
            select(ResumeVersion)
            .join(Resume, Resume.id == ResumeVersion.resume_id)
            .where(ResumeVersion.id == resume_version_id, Resume.user_id == user.id)
        )

    def generate_from_resume_version(self, db: Session, user: User, resume_version_id: int) -> Portfolio | None:
        resume_version = self.get_user_resume_version(db, user, resume_version_id)
        if resume_version is None:
            return None

        portfolio = self.get_user_portfolio(db, user)
        values = self._resume_values(resume_version)
        if portfolio is None:
            portfolio = Portfolio(user_id=user.id, slug=self._make_slug(user), **values)
            db.add(portfolio)
            db.flush()
        else:
            for key, value in values.items():
                setattr(portfolio, key, value)

        self._create_version(db, portfolio, resume_version.id)
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(portfolio)
        return portfolio

    def update_portfolio(self, db: Session, user: User, portfolio_id: int, update: PortfolioUpdate) -> Portfolio | None:
        portfolio = self.get_portfolio(db, user, portfolio_id)
        if portfolio is None:
            return None

        for field, value in update.model_dump(exclude_unset=True).items():
            setattr(portfolio, field, value)

        self._create_version(db, portfolio, self._latest_source_resume_version_id(db, portfolio.id))
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(portfolio)
        return portfolio

    def _resume_values(self, resume: ResumeVersion) -> dict:
        return {
            "headline": resume.full_name,
            "bio": resume.summary,
            "email": resume.email,
            "phone": resume.phone,
            "location": resume.location,
            "linkedin_url": resume.linkedin_url,
            "github_url": resume.github_url,
            "skills": self._as_text_list(resume.skills),
            "experience": self._as_text_list(resume.experience),
            "education": self._as_text_list(resume.education),
            "projects": self._as_text_list(resume.projects),
            "certifications": self._as_text_list(resume.certifications),
            "achievements": self._as_text_list(resume.achievements),
        }

    def _as_text_list(self, value: object) -> list[str] | None:
        if value is None:
            return None
        if not isinstance(value, list):
            return [str(value)]

        items: list[str] = []
        for item in value:
            if isinstance(item, str):
                text = item.strip()
            elif isinstance(item, dict):
                text = " — ".join(
                    str(item[key]).strip()
                    for key in ("title", "company", "role", "description")
                    if item.get(key)
                ) or str(item)
            else:
                text = str(item).strip()
            if text:
                items.append(text)
        return items or None

    def _make_slug(self, user: User) -> str:
        base = re.sub(r"[^a-z0-9]+", "-", user.full_name.lower()).strip("-") or "profile"
        return f"{base}-{user.id}"

    def _latest_source_resume_version_id(self, db: Session, portfolio_id: int) -> int | None:
        return db.scalar(
            select(PortfolioVersion.source_resume_version_id)
            .where(PortfolioVersion.portfolio_id == portfolio_id)
            .order_by(PortfolioVersion.version_number.desc())
            .limit(1)
        )

    def _create_version(self, db: Session, portfolio: Portfolio, source_resume_version_id: int | None) -> None:
        latest = db.scalar(
            select(PortfolioVersion.version_number)
            .where(PortfolioVersion.portfolio_id == portfolio.id)
            .order_by(PortfolioVersion.version_number.desc())
            .limit(1)
        )
        snapshot = {
            key: getattr(portfolio, key)
            for key in (
                "headline", "bio", "email", "phone", "location", "linkedin_url", "github_url",
                "skills", "experience", "education", "projects", "certifications", "achievements",
                "theme", "is_published",
            )
        }
        db.add(PortfolioVersion(
            portfolio_id=portfolio.id,
            version_number=(latest or 0) + 1,
            source_resume_version_id=source_resume_version_id,
            snapshot=snapshot,
        ))
