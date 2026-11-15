"""Application configuration using Pydantic Settings."""

import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _env_files() -> tuple[str, ...]:
    """
    Resolve which env files to load, in increasing order of priority.

    `.env` is the conventional name and wins, so `cp .env.example .env` just works.
    `.env.dev` / `.env.prod` are still honoured for existing deployments, and
    `ENV_FILE` overrides everything.
    """
    explicit = os.getenv("ENV_FILE")
    if explicit:
        return (explicit,)

    env = os.getenv("ENVIRONMENT", "development").lower()
    legacy = ".env.prod" if env == "production" else ".env.dev"
    return (legacy, ".env")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    PROJECT_NAME: str = "Arabic Semantic Game API"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: str | None = None

    # Database
    DATABASE_URL: str

    # CORS: localhost only by default. Add your own deployed frontend via the
    # CORS_ORIGINS env var; a fork should never inherit someone else's origins.
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # ML Model
    ML_MODEL_NAME: str = "silma-ai/silma-embedding-matryoshka-v0.1"

    # Word seeding. The sample file ships with the repo; point this at your own
    # list to seed a real deployment. See docs/word-pool.md.
    WORD_SEED_FILE: str = "data/words.sample.json"

    # Hints
    MAX_HINTS_PER_USER: int = 3

    # Rate limiting: requires Redis when enabled.
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_STORAGE_URI: str = "redis://localhost:6379"

    model_config = SettingsConfigDict(
        env_file=_env_files(),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Global settings instance
settings = Settings()
