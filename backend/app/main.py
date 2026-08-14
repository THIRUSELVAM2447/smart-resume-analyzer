from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
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


# Allow the configured frontend origins to communicate with the API.
# CORS configuration is controlled centrally through application settings.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Authentication routes.
# auth.py already defines the /api/auth prefix.
app.include_router(auth_router)


@app.get("/")
def read_root() -> dict:
    """Root health/status endpoint."""
    return {
        "message": "ResumeIQ API is running",
        "status": "ok",
    }


@app.get("/health")
def health_check() -> dict:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
    }