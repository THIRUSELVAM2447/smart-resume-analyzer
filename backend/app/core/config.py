# backend/app/core/config.py

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


class Settings(BaseSettings):
    """
    Centralized application configuration.

    Values are loaded from environment variables (or backend/.env
    during development). This class only DECLARES what config exists
    and its types — it does not connect to a database, issue JWTs,
    or define any routes.
    """

    # ---------- Application ----------
    APP_NAME: str = "ResumeIQ"
    ENVIRONMENT: str = "development"  # e.g. development | staging | production

    # ---------- Database ----------
    DATABASE_URL: str  # required — no default, must be set via env/.env

    # ---------- Authentication ----------
    JWT_SECRET_KEY: str  # required — never hard-code this
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ---------- AI (Groq) ----------
    GROQ_API_KEY: str  # required — never hard-code this
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # ---------- CORS ----------
    CORS_ORIGINS: str = "http://localhost:5173"

    # ---------- Resume upload ----------
    MAX_RESUME_SIZE_MB: int = 5

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS_ORIGINS as a clean Python list, split from a comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.

    Using lru_cache means Settings() is only constructed once (and the
    .env file only read once), even if get_settings() is called from
    many different modules.
    """
    return Settings()


settings = get_settings()