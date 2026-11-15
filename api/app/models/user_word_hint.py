"""UserWordHint model."""

from sqlalchemy import Column, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class UserWordHint(Base):
    """User's hints for a word."""

    __tablename__ = "user_word_hints"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    word_hint_id = Column(
        Integer, ForeignKey("word_hints.id", ondelete="CASCADE"), nullable=False, index=True
    )
    daily_word_id = Column(
        Integer, ForeignKey("daily_words.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationships

    # Constraints and Indexes
    __table_args__ = (
        Index("ix_user_word_hints_user_hint_daily", "user_id", "word_hint_id", "daily_word_id"),
    )

    def __repr__(self):
        return f"<UserWordHint(user_id={self.user_id}, word_hint_id={self.word_hint_id}, daily_word_id={self.daily_word_id})>"
