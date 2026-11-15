"""CRUD operations for UserGuess model."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.user_guess import UserGuess


class CRUDUserGuess(CRUDBase[UserGuess, UserGuess, UserGuess]):
    """CRUD operations for UserGuess model."""

    async def get_user_guesses(
        self, db: AsyncSession, user_id: UUID, daily_word_id: int
    ) -> list[UserGuess]:
        """
        Get a user's guesses for a daily word, oldest first.

        Chronological order is what makes attempt_number meaningful; the client
        sorts by score for display.
        """
        result = await db.execute(
            select(UserGuess)
            .where(UserGuess.user_id == user_id, UserGuess.daily_word_id == daily_word_id)
            .order_by(UserGuess.created_at, UserGuess.id)
            .limit(1000)
        )
        return list(result.scalars().all())

    async def count_attempts(self, db: AsyncSession, user_id: UUID, daily_word_id: int) -> int:
        """Count total attempts for a user on a specific daily word."""
        result = await db.execute(
            select(func.count(UserGuess.id)).where(
                UserGuess.user_id == user_id, UserGuess.daily_word_id == daily_word_id
            )
        )
        return result.scalar_one()

    async def has_won(self, db: AsyncSession, user_id: UUID, daily_word_id: int) -> bool:
        """Check if user has won (guessed correctly)."""
        result = await db.execute(
            select(UserGuess)
            .where(
                UserGuess.user_id == user_id,
                UserGuess.daily_word_id == daily_word_id,
                UserGuess.is_correct.is_(True),
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def get_winning_guess(
        self, db: AsyncSession, user_id: UUID, daily_word_id: int
    ) -> UserGuess | None:
        """Get the winning guess for a user."""
        result = await db.execute(
            select(UserGuess)
            .where(
                UserGuess.user_id == user_id,
                UserGuess.daily_word_id == daily_word_id,
                UserGuess.is_correct.is_(True),
            )
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_user_guess_by_user_id_and_daily_word_id_and_guessed_word(
        self, db: AsyncSession, user_id: UUID, daily_word_id: int, guessed_word: str
    ) -> UserGuess | None:
        """Get a guess by user_id and daily_word_id."""
        result = await db.execute(
            select(UserGuess)
            .where(
                UserGuess.user_id == user_id,
                UserGuess.daily_word_id == daily_word_id,
                UserGuess.guessed_word == guessed_word,
            )
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create_guess(
        self,
        db: AsyncSession,
        user_id: UUID,
        daily_word_id: int,
        guessed_word: str,
        similarity_score: float,
        cosine_similarity: float,
        is_correct: bool = False,
        is_given_up: bool = False,
    ) -> UserGuess:
        """Create a new guess."""
        guess = UserGuess(
            user_id=user_id,
            daily_word_id=daily_word_id,
            guessed_word=guessed_word,
            similarity_score=similarity_score,
            cosine_similarity=cosine_similarity,
            is_correct=is_correct,
            is_given_up=is_given_up,
        )
        db.add(guess)
        await db.flush()
        await db.refresh(guess)
        return guess


user_guess = CRUDUserGuess(UserGuess)
