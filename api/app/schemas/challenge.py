"""Challenge-related schemas."""

from datetime import date

from pydantic import BaseModel, ConfigDict


class ChallengeResponse(BaseModel):
    """Response for a daily challenge."""

    date: date
    game_number: int
    has_challenge: bool
    word: str | None = None  # Only shown after the user wins
    hints: list[str] | None = None

    model_config = ConfigDict(from_attributes=True)
