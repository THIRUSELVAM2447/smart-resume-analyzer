# backend/app/api/resume.py

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.resume import Resume, ResumeVersion
from app.models.user import User
from app.schemas.resume import (
    ResumeDetailResponse,
    ResumeResponse,
    ResumeVersionResponse,
)
from app.services.resume_service import (
    ResumeFileNotFoundError,
    ResumeProcessingError,
    ResumeService,
)

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])

resume_service = ResumeService()

ALLOWED_CONTENT_TYPES = {"application/pdf"}
UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1 MB


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
async def create_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resume:
    """
    Upload a PDF resume for the authenticated user.

    Validates the file is a PDF, reads its contents, and delegates
    storage plus Resume record creation to
    ResumeService.create_resume_with_file(). No parsing happens here —
    that remains a separate step via POST /{resume_id}/process.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed.",
        )

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed.",
        )

    max_size_bytes = settings.MAX_RESUME_SIZE_MB * 1024 * 1024
    content = bytearray()

    while True:
        chunk = await file.read(UPLOAD_CHUNK_SIZE)
        if not chunk:
            break
        content.extend(chunk)
        if len(content) > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=(
                    f"Resume file exceeds the maximum allowed size of "
                    f"{settings.MAX_RESUME_SIZE_MB}MB."
                ),
            )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    return resume_service.create_resume_with_file(
        db=db,
        user=current_user,
        original_filename=file.filename or "resume.pdf",
        file_content=bytes(content),
    )


@router.post(
    "/{resume_id}/process",
    response_model=ResumeVersionResponse,
)
def process_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeVersion:
    """
    Extract text from a resume's stored PDF and create a new
    ResumeVersion containing it.

    Returns 404 when the resume doesn't exist or belongs to another
    user. Returns 404 when the stored file is missing, and 422 when
    the PDF cannot be processed or contains no extractable text.
    """
    try:
        version = resume_service.process_resume(db, current_user, resume_id)
    except ResumeFileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file not found.",
        )
    except ResumeProcessingError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    if version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )
    return version


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