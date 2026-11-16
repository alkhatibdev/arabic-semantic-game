"""Guess-related schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.config import MAX_GUESS_LENGTH


class GuessRequest(BaseModel):
    """Request to submit a guess."""

    user_id: UUID
    challenge_date: date
    # Bounded on purpose: an unbounded string here reached the embedding model
    # and the database verbatim. Whitespace is NOT stripped by the validator -
    # the endpoint still rejects an all-whitespace word with a 400, and a 422
    # from here would change that contract.
    word: str = Field(max_length=MAX_GUESS_LENGTH)


class GiveUpRequest(BaseModel):
    """Request to give up on a challenge."""

    user_id: UUID
    challenge_date: date


class GuessResponse(BaseModel):
    """Response for a guess."""

    id: int
    word: str
    similarity_score: float
    cosine_similarity: float
    is_correct: bool
    attempt_number: int  # Calculated dynamically
    created_at: datetime
    is_given_up: bool = False

    model_config = ConfigDict(from_attributes=True)
