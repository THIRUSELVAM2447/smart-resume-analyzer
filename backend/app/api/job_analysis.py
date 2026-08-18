# backend/app/api/job_analysis.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.job_analysis import JobAnalysis
from app.models.user import User
from app.schemas.job_analysis import (
    JobAnalysisCreate,
    JobAnalysisResponse,
)
from app.services.job_analysis_service import JobAnalysisService


router = APIRouter(
    prefix="/api/job-analyses",
    tags=["Job Analysis"],
)

job_analysis_service = JobAnalysisService()


# ---------------------------------------------------------------------------
# CREATE ATS ANALYSIS
# ---------------------------------------------------------------------------

@router.post(
    "/jobs/{job_id}/analyze",
    response_model=JobAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
)
def analyze_job(
    job_id: int,
    analysis_data: JobAnalysisCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobAnalysis:
    """
    Analyze a job against a specific resume version.

    Both the Job and ResumeVersion must belong to
    the authenticated user.
    """

    analysis = job_analysis_service.analyze_job(
        db=db,
        user=current_user,
        job_id=job_id,
        resume_version_id=analysis_data.resume_version_id,
    )

    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job or resume version not found.",
        )

    return analysis


# ---------------------------------------------------------------------------
# GET ALL ANALYSES FOR A JOB
# ---------------------------------------------------------------------------

@router.get(
    "/jobs/{job_id}",
    response_model=list[JobAnalysisResponse],
)
def get_job_analyses(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[JobAnalysis]:
    """
    Get all ATS analyses performed for a specific job.

    The job must belong to the authenticated user.
    """

    analyses = job_analysis_service.get_job_analyses(
        db=db,
        user=current_user,
        job_id=job_id,
    )

    if analyses is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )

    return analyses


# ---------------------------------------------------------------------------
# GET ONE ANALYSIS
# ---------------------------------------------------------------------------

@router.get(
    "/{analysis_id}",
    response_model=JobAnalysisResponse,
)
def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobAnalysis:
    """
    Get one previously created ATS analysis.

    The analysis is returned only when the related job
    belongs to the authenticated user.
    """

    analysis = job_analysis_service.get_analysis(
        db=db,
        user=current_user,
        analysis_id=analysis_id,
    )

    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    return analysis