"""DailyWord model."""

from datetime import datetime, timezone

from sqlalchemy import Column, Date, DateTime, Index, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class DailyWord(Base):
    """Daily word challenge model."""

    __tablename__ = "daily_words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, nullable=False, index=True)
    date = Column(Date, unique=True, nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    guesses = relationship("UserGuess", back_populates="daily_word", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("ix_daily_words_date", "date"),
        Index("ix_daily_words_word", "word"),
    )

    def __repr__(self):
        return f"<DailyWord(date={self.date}, word={self.word})>"
