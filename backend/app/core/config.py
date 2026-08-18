from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Resolve backend/.env regardless of the current working directory.
# __file__ = backend/app/core/config.py
# .parents[0] = backend/app/core
# .parents[1] = backend/app
# .parents[2] = backend
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE_PATH = BASE_DIR / ".env"

DEFAULT_UPLOAD_DIR = BASE_DIR / "uploads" / "resumes"


class Settings(BaseSettings):
    """
    Centralized application configuration.

    Values are loaded from environment variables or backend/.env
    during development.
    """

    # ---------- Application ----------
    APP_NAME: str = "ResumeIQ"
    ENVIRONMENT: str = "development"

    # ---------- Database ----------
    DATABASE_URL: str

    # ---------- Authentication ----------
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ---------- AI (Groq) ----------
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # ---------- CORS ----------
    CORS_ORIGINS: str = "http://localhost:5173"

    # ---------- Resume upload ----------
    MAX_RESUME_SIZE_MB: int = 5
    UPLOAD_DIR: Path = DEFAULT_UPLOAD_DIR

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Convert CORS_ORIGINS into a clean list."""
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance.
    """
    return Settings()


settings = get_settings()