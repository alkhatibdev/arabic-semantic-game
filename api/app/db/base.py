"""Import all models here for Alembic autogenerate to work."""

from app.db.session import Base
from app.models.daily_word import DailyWord

# Import all models so Alembic can detect them
from app.models.user import User
from app.models.user_guess import UserGuess
from app.models.user_word_hint import UserWordHint
from app.models.word_hint import WordHint

__all__ = ["Base", "User", "DailyWord", "WordHint", "UserGuess", "UserWordHint"]
