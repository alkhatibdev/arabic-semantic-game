"""Guess-related schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GuessRequest(BaseModel):
    """Request to submit a guess."""

    user_id: UUID
    challenge_date: date
    word: str


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
