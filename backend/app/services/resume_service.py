import uuid
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.resume import Resume, ResumeVersion
from app.models.user import User
from app.schemas.resume import ResumeBase
from app.services.pdf_service import PDFExtractionError, PDFService
from app.services.resume_parser_service import ResumeParserService


class ResumeFileNotFoundError(Exception):
    """
    Raised when a Resume's stored file cannot be found on disk during
    processing.
    """

    pass


class ResumeProcessingError(Exception):
    """
    Raised when a resume's PDF cannot be extracted, or extraction
    produces no meaningful text.
    """

    pass


pdf_service = PDFService()
resume_parser_service = ResumeParserService()


class ResumeService:
    """
    Resume and ResumeVersion service.

    Contains resume-related business/data-access logic only. Receives
    a SQLAlchemy Session and the authenticated User from the caller on
    every method — never creates its own session, never raises
    HTTP-level exceptions, and never operates outside the scope of the
    authenticated user's own resumes.
    """

    def get_user_resumes(
        self,
        db: Session,
        user: User,
    ) -> list[Resume]:
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
        self,
        db: Session,
        user: User,
        resume_id: int,
    ) -> Resume | None:
        """
        Return a single resume, only if it belongs to the authenticated
        user.

        Returns None if the resume does not exist or belongs to someone
        else.
        """
        stmt = select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == user.id,
        )

        return db.scalar(stmt)

    def get_resume_detail(
        self,
        db: Session,
        user: User,
        resume_id: int,
    ) -> Resume | None:
        """
        Return a resume with its version history available through the
        existing Resume.versions relationship.
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
        resume = self.get_resume(
            db,
            user,
            resume_id,
        )

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
        user, without handling any file storage.

        Retained for metadata-only creation. The real upload flow uses
        create_resume_with_file() instead.
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

    def create_resume_with_file(
        self,
        db: Session,
        user: User,
        original_filename: str,
        file_content: bytes,
    ) -> Resume:
        """
        Save an uploaded PDF to storage and create the corresponding
        Resume database record.

        The file is written to disk using a generated UUID-based
        filename — never the client-supplied filename — to avoid path
        traversal and filename collisions.

        original_filename is stored separately, purely as display
        metadata.

        If the database commit fails after the file has already been
        written, the file is removed so storage and the database do
        not drift out of sync.
        """
        settings.UPLOAD_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        stored_filename = f"{uuid.uuid4().hex}.pdf"
        stored_path = settings.UPLOAD_DIR / stored_filename

        stored_path.write_bytes(file_content)

        new_resume = Resume(
            user_id=user.id,
            original_filename=original_filename,
            file_path=str(stored_path),
            is_active=True,
        )

        db.add(new_resume)

        try:
            db.commit()
        except Exception:
            db.rollback()
            stored_path.unlink(missing_ok=True)
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
        to the authenticated user.

        Never overwrites an existing version. The new version_number
        is derived from the current highest version_number.
        """
        resume = self.get_resume(
            db,
            user,
            resume_id,
        )

        if resume is None:
            return None

        next_version_number = self._get_next_version_number(
            db,
            resume_id,
        )

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

    def process_resume(
        self,
        db: Session,
        user: User,
        resume_id: int,
    ) -> ResumeVersion | None:
        """
        Extract text from a resume's stored PDF, parse it into
        structured fields via ResumeParserService, and create a new
        ResumeVersion containing both the raw text and parsed fields.

        Returns None if the resume doesn't exist or doesn't belong to
        the authenticated user.

        Raises:
            ResumeFileNotFoundError:
                If the resume's stored file is missing.

            ResumeProcessingError:
                If the PDF cannot be extracted or extraction produces
                no meaningful text.
        """
        resume = self.get_resume(
            db,
            user,
            resume_id,
        )

        if resume is None:
            return None

        if (
            not resume.file_path
            or not Path(resume.file_path).exists()
        ):
            raise ResumeFileNotFoundError(
                "The stored resume file could not be found."
            )

        try:
            raw_text = pdf_service.extract_text(
                resume.file_path
            )
        except PDFExtractionError as exc:
            raise ResumeProcessingError(
                str(exc)
            ) from exc

        if not raw_text.strip():
            raise ResumeProcessingError(
                "No meaningful text could be extracted from this PDF."
            )

        # Parse the extracted resume text into structured fields.
        parsed = resume_parser_service.parse(raw_text)

        # Reuse the existing ResumeVersion creation method.
        # This preserves ownership checking, version numbering,
        # transaction handling, and database persistence in one place.
        return self.create_resume_version(
            db=db,
            user=user,
            resume_id=resume_id,
            raw_text=raw_text,
            full_name=parsed["full_name"],
            email=parsed["email"],
            phone=parsed["phone"],
            location=parsed["location"],
            linkedin_url=parsed["linkedin_url"],
            github_url=parsed["github_url"],
            summary=parsed["summary"],
            skills=parsed["skills"],
            experience=parsed["experience"],
            education=parsed["education"],
            projects=parsed["projects"],
            certifications=parsed["certifications"],
            achievements=parsed["achievements"],
        )

    def deactivate_resume(
        self,
        db: Session,
        user: User,
        resume_id: int,
    ) -> Resume | None:
        """
        Mark a resume as inactive without deleting it.
        """
        resume = self.get_resume(
            db,
            user,
            resume_id,
        )

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

    def _get_next_version_number(
        self,
        db: Session,
        resume_id: int,
    ) -> int:
        """
        Return the next version number for a resume.
        """
        stmt = select(
            func.max(ResumeVersion.version_number)
        ).where(
            ResumeVersion.resume_id == resume_id
        )

        highest = db.scalar(stmt)

        return (highest or 0) + 1