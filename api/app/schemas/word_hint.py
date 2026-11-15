"""Word hint-related schemas."""

from pydantic import BaseModel, ConfigDict


class WordHintsRequest(BaseModel):
    """Response for word hints."""

    hints: list[str]
    word: str

    model_config = ConfigDict(from_attributes=True)


class WordHintResponse(BaseModel):
    """Response for a word hint."""

    hint_text: str
    hint_order: int

    model_config = ConfigDict(from_attributes=True)
