"""WordHint model."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Index, Integer, String

from app.db.session import Base


class WordHint(Base):
    """Hints for daily words."""

    __tablename__ = "word_hints"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, nullable=False, index=True)  # Links to daily_words.word
    hint_text = Column(String, nullable=False)
    hint_order = Column(Integer, nullable=False, default=0)
    generated_by = Column(String, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Constraints and Indexes
    __table_args__ = (
        Index(
            "ix_word_hints_word_order", "word", "hint_order"
        ),  # Composite index for fast retrieval
    )

    def __repr__(self):
        return f"<WordHint(word={self.word}, order={self.hint_order})>"
