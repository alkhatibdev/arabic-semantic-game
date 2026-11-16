"""UserGuess model."""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.config import MAX_GUESS_LENGTH
from app.db.session import Base


class UserGuess(Base):
    """User's guesses for daily word challenges."""

    __tablename__ = "user_guesses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    daily_word_id = Column(
        Integer, ForeignKey("daily_words.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Length-capped to match the API schema. guessed_word is part of the
    # uq_user_daily_word_guess btree index, and Postgres refuses an index entry
    # over ~2704 bytes, so an unbounded column turned a long guess into a 500.
    guessed_word = Column(String(MAX_GUESS_LENGTH), nullable=False)
    similarity_score = Column(Float, nullable=False)
    cosine_similarity = Column(Float, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    is_given_up = Column(Boolean, default=False, nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="guesses")
    daily_word = relationship("DailyWord", back_populates="guesses")

    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint(
            "user_id", "daily_word_id", "guessed_word", name="uq_user_daily_word_guess"
        ),
        Index(
            "ix_user_guesses_user_daily_created", "user_id", "daily_word_id", "created_at"
        ),  # Critical composite
        Index("ix_user_guesses_daily_created", "daily_word_id", "created_at"),  # For analytics
    )

    def __repr__(self):
        return f"<UserGuess(user_id={self.user_id}, word={self.guessed_word}, correct={self.is_correct})>"
