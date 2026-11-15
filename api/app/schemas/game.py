"""Game-related schemas."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.guess import GuessResponse
from app.schemas.word_hint import WordHintResponse


class GameStatusResponse(BaseModel):
    """Response for game status."""

    won: bool
    attempts: int
    won_at: datetime | None = None
    target_word: str | None = None  # Only if won

    model_config = ConfigDict(from_attributes=True)


class GameStateResponse(BaseModel):
    """Response for complete game state."""

    challenge_date: date
    game_number: int
    guesses: list[GuessResponse]
    game_status: GameStatusResponse | None = None
    has_won: bool = False
    hints: list[WordHintResponse] = Field(default_factory=list)
    max_hints: int = 3

    model_config = ConfigDict(from_attributes=True)
