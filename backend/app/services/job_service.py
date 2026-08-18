# backend/app/services/job_service.py

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobUpdate


class JobService:
    """
    Job-related business and data-access logic.

    All operations are scoped to the authenticated user's own jobs.
    The service never raises HTTP-level exceptions.
    """

    def get_user_jobs(
        self,
        db: Session,
        user: User,
    ) -> list[Job]:
        """
        Return all jobs belonging to the authenticated user,
        newest first.
        """

        stmt = (
            select(Job)
            .where(Job.user_id == user.id)
            .order_by(Job.created_at.desc())
        )

        return list(db.scalars(stmt).all())

    def get_job(
        self,
        db: Session,
        user: User,
        job_id: int,
    ) -> Job | None:
        """
        Return a single job only when it belongs to the
        authenticated user.

        Returns None when the job does not exist or belongs
        to another user.
        """

        stmt = select(Job).where(
            Job.id == job_id,
            Job.user_id == user.id,
        )

        return db.scalar(stmt)

    def create_job(
        self,
        db: Session,
        user: User,
        job_data: JobCreate,
    ) -> Job:
        """
        Create a new job belonging to the authenticated user.
        """

        new_job = Job(
            user_id=user.id,
            title=job_data.title,
            company_name=job_data.company_name,
            source_url=job_data.source_url,
            description=job_data.description,
            source_type=job_data.source_type,
        )

        db.add(new_job)

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(new_job)

        return new_job

    def update_job(
        self,
        db: Session,
        user: User,
        job_id: int,
        job_data: JobUpdate,
    ) -> Job | None:
        """
        Update an existing job belonging to the authenticated user.

        Only fields explicitly supplied by the caller are changed.
        """

        job = self.get_job(
            db,
            user,
            job_id,
        )

        if job is None:
            return None

        update_data = job_data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(job, field, value)

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(job)

        return job