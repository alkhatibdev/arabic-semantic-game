"""Similarity calculation service using ML model."""

import math
import re

from sklearn.metrics.pairwise import cosine_similarity
from starlette.concurrency import run_in_threadpool

from app.core.ml_model import model_loader

_LATIN_RE = re.compile(r"[a-zA-Z]")


class SimilarityService:
    """Service for calculating word similarity using ML embeddings."""

    @property
    def model(self):
        """
        The embedding model, resolved on first use.

        Reading it in __init__ would trigger a multi-hundred-megabyte download at
        import time - including when Alembic imports anything in this chain.
        """
        return model_loader.model

    def contains_english_chars(self, word: str) -> bool:
        """Whether a word contains Latin letters (a-z, A-Z)."""
        return bool(_LATIN_RE.search(word))

    def scale_similarity(self, cos_sim: float) -> float:
        """
        Map a cosine similarity in [-1, 1] onto a 0-100 player-facing score.

        Squaring the normalised value keeps early guesses feeling far away and
        makes the last few points the hard ones.
        """
        x = (cos_sim + 1) / 2
        return math.pow(x, 2) * 100

    def calculate_similarity(self, word1: str, word2: str) -> tuple[float, float]:
        """
        Calculate similarity between two words.

        Returns:
            (similarity_score in 0-100, raw cosine similarity in -1..1)
        """
        # The model is Arabic; Latin input is out of domain, so score it as 0
        # rather than returning a meaningless embedding distance.
        if self.contains_english_chars(word1) or self.contains_english_chars(word2):
            return 0.0, 0.0

        embedding1 = self.model.encode(word1, convert_to_numpy=True)
        embedding2 = self.model.encode(word2, convert_to_numpy=True)

        cos_sim = float(cosine_similarity([embedding1], [embedding2])[0][0])

        return self.scale_similarity(cos_sim), cos_sim

    async def calculate_similarity_async(self, word1: str, word2: str) -> tuple[float, float]:
        """
        Async wrapper around calculate_similarity.

        model.encode() is a synchronous CPU-bound call; awaiting it inline would
        stall the whole worker, so it runs in a thread.
        """
        if self.contains_english_chars(word1) or self.contains_english_chars(word2):
            return 0.0, 0.0
        return await run_in_threadpool(self.calculate_similarity, word1, word2)


# Global similarity service instance. Cheap to construct - the model itself is
# loaded lazily via the `model` property.
similarity_service = SimilarityService()
