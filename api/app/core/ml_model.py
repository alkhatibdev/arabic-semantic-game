"""ML model loading and management."""

import logging
from typing import TYPE_CHECKING, Optional

from app.core.config import settings

if TYPE_CHECKING:  # pragma: no cover
    from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class ModelLoader:
    """Singleton that loads and caches the embedding model."""

    _instance: Optional["ModelLoader"] = None
    _model: Optional["SentenceTransformer"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_model(self) -> "SentenceTransformer":
        """Load the sentence transformer model (cached after the first call)."""
        if self._model is None:
            # Imported here, not at module scope: pulling in sentence_transformers
            # drags in torch, which Alembic, the seed scripts and the test suite
            # have no use for.
            from sentence_transformers import SentenceTransformer

            logger.info("Loading embedding model: %s", settings.ML_MODEL_NAME)
            self._model = SentenceTransformer(settings.ML_MODEL_NAME)
            logger.info("Embedding model loaded")
        return self._model

    @property
    def model(self) -> "SentenceTransformer":
        """The loaded model, loading it on first access."""
        if self._model is None:
            return self.load_model()
        return self._model


# Global model loader instance
model_loader = ModelLoader()
