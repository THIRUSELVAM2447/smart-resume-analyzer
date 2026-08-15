# backend/app/services/resume_service.py

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.resume import Resume, ResumeVersion
from app.models.user import User
from app.schemas.resume import ResumeBase


class ResumeService:
    """
    Resume and ResumeVersion service.

    Contains resume-related business/data-access logic only. Receives
    a SQLAlchemy Session and the authenticated User from the caller on
    every method — never creates its own session, never raises
    HTTP-level exceptions, and never operates outside the scope of the
    authenticated user's own resumes.
    """

    def get_user_resumes(self, db: Session, user: User) -> list[Resume]:
        """
        Return all resumes belonging to the authenticated user,
        newest first.
        """
        stmt = (
            select(Resume)
            .where(Resume.user_id == user.id)
            .order_by(Resume.created_at.desc())
        )
        return list(db.scalars(stmt).all())

    def get_resume(
        self, db: Session, user: User, resume_id: int
    ) -> Resume | None:
        """
        Return a single resume, only if it belongs to the authenticated
        user. Returns None if it doesn't exist or belongs to someone
        else.
        """
        stmt = select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == user.id,
        )
        return db.scalar(stmt)

    def get_resume_detail(
        self, db: Session, user: User, resume_id: int
    ) -> Resume | None:
        """
        Return a resume (with its versions available via the existing
        Resume.versions relationship) for the authenticated user only.

        Serialization into ResumeDetailResponse happens at the API
        layer, not here.
        """
        return self.get_resume(db, user, resume_id)

    def get_resume_version(
        self,
        db: Session,
        user: User,
        resume_id: int,
        version_number: int,
    ) -> ResumeVersion | None:
        """
        Return one specific ResumeVersion of a resume belonging to the
        authenticated user.

        Returns None if the resume doesn't exist, doesn't belong to
        the user, or has no version with the given version_number.
        """
        resume = self.get_resume(db, user, resume_id)
        if resume is None:
            return None

        stmt = select(ResumeVersion).where(
            ResumeVersion.resume_id == resume.id,
            ResumeVersion.version_number == version_number,
        )
        return db.scalar(stmt)

    def create_resume(
        self,
        db: Session,
        user: User,
        resume_data: ResumeBase,
        file_path: str = "",
    ) -> Resume:
        """
        Create a Resume metadata row belonging to the authenticated
        user.

        Does not handle the uploaded file itself — file_path defaults
        to an empty placeholder here and is expected to be populated
        by the future file-upload/storage step.
        """
        new_resume = Resume(
            user_id=user.id,
            original_filename=resume_data.original_filename,
            file_path=file_path,
            is_active=True,
        )

        db.add(new_resume)
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(new_resume)
        return new_resume

    def create_resume_version(
        self,
        db: Session,
        user: User,
        resume_id: int,
        raw_text: str,
        full_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        location: str | None = None,
        linkedin_url: str | None = None,
        github_url: str | None = None,
        summary: str | None = None,
        skills: dict | list | None = None,
        experience: dict | list | None = None,
        education: dict | list | None = None,
        projects: dict | list | None = None,
        certifications: dict | list | None = None,
        achievements: dict | list | None = None,
    ) -> ResumeVersion | None:
        """
        Create a new, immutable ResumeVersion for an existing resume
        belonging to the authenticated user.

        Returns None if the resume does not exist or does not belong
        to the authenticated user. Never overwrites an existing
        version; the new version_number is derived from the current
        highest version_number for this resume.
        """
        resume = self.get_resume(db, user, resume_id)
        if resume is None:
            return None

        next_version_number = self._get_next_version_number(db, resume_id)

        new_version = ResumeVersion(
            resume_id=resume_id,
            version_number=next_version_number,
            raw_text=raw_text,
            full_name=full_name,
            email=email,
            phone=phone,
            location=location,
            linkedin_url=linkedin_url,
            github_url=github_url,
            summary=summary,
            skills=skills,
            experience=experience,
            education=education,
            projects=projects,
            certifications=certifications,
            achievements=achievements,
        )

        db.add(new_version)
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(new_version)
        return new_version

    def deactivate_resume(
        self, db: Session, user: User, resume_id: int
    ) -> Resume | None:
        """
        Mark a resume as inactive (is_active = False) without deleting
        it, preserving history. Returns None if the resume doesn't
        exist or doesn't belong to the authenticated user.
        """
        resume = self.get_resume(db, user, resume_id)
        if resume is None:
            return None

        resume.is_active = False

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(resume)
        return resume

    def _get_next_version_number(self, db: Session, resume_id: int) -> int:
        """
        Compute the next version_number for a resume: highest existing
        version_number + 1, or 1 if no versions exist yet.
        """
        stmt = select(func.max(ResumeVersion.version_number)).where(
            ResumeVersion.resume_id == resume_id
        )
        highest = db.scalar(stmt)
        return (highest or 0) + 1