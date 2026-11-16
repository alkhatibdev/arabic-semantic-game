"""Shared test fixtures."""

import os

# Settings are read at import time and DATABASE_URL is required, so it has to be
# present before anything under app/ is imported.
os.environ.setdefault("ENV_FILE", "/dev/null")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/arabic_semantic_game_test",
)
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

import numpy as np  # noqa: E402
import pytest  # noqa: E402


class FakeModel:
    """Stand-in for the sentence-transformer, so tests need no model download."""

    def __init__(self, vectors: dict[str, list[float]] | None = None) -> None:
        self.vectors = vectors or {}
        self.encode_calls: list[str] = []

    def encode(self, word, convert_to_numpy=True):
        self.encode_calls.append(word)
        # Unknown words get a deterministic vector derived from the string, so
        # distinct words are distinct but repeatable.
        vec = self.vectors.get(word)
        if vec is None:
            seed = sum(ord(c) for c in word) or 1
            vec = [seed % 7 + 1, seed % 11 + 1, seed % 13 + 1]
        return np.array(vec, dtype=np.float32)


@pytest.fixture
def fake_model(monkeypatch):
    """Install a FakeModel as the loaded embedding model."""
    from app.core.ml_model import model_loader

    model = FakeModel()
    monkeypatch.setattr(model_loader, "_model", model)
    return model


@pytest.fixture(scope="module")
def fake_model_module():
    """Module-scoped FakeModel, for the integration suite."""
    from app.core.ml_model import model_loader

    previous = model_loader._model
    model_loader._model = FakeModel()
    yield model_loader._model
    model_loader._model = previous
