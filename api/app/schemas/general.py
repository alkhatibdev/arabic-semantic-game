"""General schemas."""

from pydantic import BaseModel, ConfigDict


class BasicResponse(BaseModel):
    """Basic response."""

    success: bool
    message: str | None = ""

    model_config = ConfigDict(from_attributes=True)
