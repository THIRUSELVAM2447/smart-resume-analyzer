from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.job import router as job_router
from app.api.job_analysis import router as job_analysis_router
from app.api.resume import router as resume_router
from app.core.config import settings


app = FastAPI(
    title="ResumeIQ API",
    description=(
        "ResumeIQ is an AI-powered resume analysis and portfolio-generation "
        "platform. It analyzes resumes against job postings and generates "
        "a synchronized personal portfolio from resume content."
    ),
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# API ROUTERS
# ---------------------------------------------------------------------------

# Authentication
app.include_router(auth_router)

# Resume upload, processing, versions and management
app.include_router(resume_router)

# Job posting creation, listing and management
app.include_router(job_router)

# ATS job analysis
app.include_router(job_analysis_router)


# ---------------------------------------------------------------------------
# ROOT ENDPOINT
# ---------------------------------------------------------------------------

@app.get("/")
def read_root() -> dict:
    """Root health/status endpoint."""

    return {
        "message": "ResumeIQ API is running",
        "status": "ok",
    }


# ---------------------------------------------------------------------------
# HEALTH ENDPOINT
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check() -> dict:
    """Basic health check endpoint."""

    return {
        "status": "healthy",
    }