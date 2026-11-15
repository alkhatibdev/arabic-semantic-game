"""Tests for settings resolution."""

import os

from app.core.config import _env_files, settings


def test_dot_env_is_honoured_and_wins():
    """
    `cp .env.example .env` has to work.

    This used to load only `.env.dev`, so the conventional filename was silently
    ignored and startup failed with an opaque validation error.
    """
    os.environ.pop("ENV_FILE", None)
    files = _env_files()
    assert ".env" in files
    assert files[-1] == ".env", "`.env` must have the highest priority"


def test_explicit_env_file_overrides():
    os.environ["ENV_FILE"] = ".env.staging"
    try:
        assert _env_files() == (".env.staging",)
    finally:
        os.environ["ENV_FILE"] = "/dev/null"


def test_cors_default_is_localhost_only():
    """A fork must not inherit anyone else's production origin."""
    from app.core.config import Settings

    defaults = Settings.model_fields["CORS_ORIGINS"].default_factory()
    assert defaults == ["http://localhost:3000"]


def test_sentry_is_off_by_default():
    assert settings.SENTRY_DSN in (None, "")
