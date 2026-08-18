# backend/app/schemas/job_analysis.py

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobAnalysisCreate(BaseModel):
    """
    Input required to analyze a job against a specific ResumeVersion.
    """

    resume_version_id: int = Field(gt=0)


class JobAnalysisResponse(BaseModel):
    """
    API response representing one ATS analysis.

    The analysis compares a Job against a specific ResumeVersion.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    resume_version_id: int

    overall_score: int
    skill_score: int | None = None

    matched_skills: list | None = None
    missing_skills: list | None = None
    extra_skills: list | None = None

    grammar_issues: list | None = None
    recommendations: list | None = None

    analysis_snapshot: dict | None = None

    created_at: datetime