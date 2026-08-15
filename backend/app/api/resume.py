# backend/app/api/resume.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.resume import Resume, ResumeVersion
from app.models.user import User
from app.schemas.resume import (
    ResumeBase,
    ResumeDetailResponse,
    ResumeResponse,
    ResumeVersionResponse,
)
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])

resume_service = ResumeService()


@router.get("", response_model=list[ResumeResponse])
def list_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Resume]:
    """List all resumes belonging to the authenticated user."""
    return resume_service.get_user_resumes(db, current_user)


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resume:
    """
    Get a single resume, including its parsed version history.

    Returns 404 both when the resume doesn't exist and when it belongs
    to another user, so ownership is never revealed to the caller.
    """
    resume = resume_service.get_resume_detail(db, current_user, resume_id)
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )
    return resume


@router.get(
    "/{resume_id}/versions/{version_number}",
    response_model=ResumeVersionResponse,
)
def get_resume_version(
    resume_id: int,
    version_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeVersion:
    """
    Get one specific parsed version of a resume belonging to the
    authenticated user.

    Returns 404 when the resume doesn't exist, belongs to another
    user, or has no version with the given version_number — the same
    response in every case, so ownership is never revealed.
    """
    version = resume_service.get_resume_version(
        db, current_user, resume_id, version_number
    )
    if version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume version not found.",
        )
    return version


@router.post(
    "",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_resume(
    resume_data: ResumeBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resume:
    """
    Create resume metadata for the authenticated user.

    Does not handle file upload/storage or parsing yet — those are
    implemented in a later step.
    """
    return resume_service.create_resume(db, current_user, resume_data)


@router.patch("/{resume_id}/deactivate", response_model=ResumeResponse)
def deactivate_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resume:
    """
    Deactivate (not delete) a resume belonging to the authenticated
    user.
    """
    resume = resume_service.deactivate_resume(db, current_user, resume_id)
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )
    return resume