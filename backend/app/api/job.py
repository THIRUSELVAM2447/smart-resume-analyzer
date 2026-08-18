# backend/app/api/job.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobResponse, JobUpdate
from app.services.job_service import JobService


router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs"],
)

job_service = JobService()


@router.get(
    "",
    response_model=list[JobResponse],
)
def list_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Job]:
    """
    List all jobs belonging to the authenticated user.
    """

    return job_service.get_user_jobs(
        db,
        current_user,
    )


@router.get(
    "/{job_id}",
    response_model=JobResponse,
)
def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Job:
    """
    Get one job belonging to the authenticated user.

    Returns the same 404 response when the job does not exist
    or belongs to another user.
    """

    job = job_service.get_job(
        db,
        current_user,
        job_id,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )

    return job


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Job:
    """
    Create a job posting for the authenticated user.
    """

    return job_service.create_job(
        db,
        current_user,
        job_data,
    )


@router.patch(
    "/{job_id}",
    response_model=JobResponse,
)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Job:
    """
    Update a job belonging to the authenticated user.
    """

    job = job_service.update_job(
        db,
        current_user,
        job_id,
        job_data,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )

    return job