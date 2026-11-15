"""CRUD operations for WordHint model."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.user_word_hint import UserWordHint
from app.models.word_hint import WordHint


class CRUDWordHint(CRUDBase[WordHint, WordHint, WordHint]):
    """CRUD operations for WordHint model."""

    async def get_hints_for_word(self, db: AsyncSession, word: str) -> list[WordHint]:
        """Get all hints for a word, ordered by hint_order."""
        result = await db.execute(
            select(WordHint).where(WordHint.word == word).order_by(WordHint.hint_order)
        )
        return list(result.scalars().all())

    async def get_word_hints_for_user(
        self, db: AsyncSession, user_id: UUID, word: str
    ) -> list[WordHint]:
        """Get all hints for a user on a specific word."""
        result = await db.execute(
            select(WordHint)
            .join(UserWordHint)
            .where(UserWordHint.user_id == user_id)
            .where(UserWordHint.word_hint_id == WordHint.id)
            .where(WordHint.word == word)
        )
        return list(result.scalars().all())

    async def get_new_hint(
        self, db: AsyncSession, word: str, not_in: list[int] | None = None
    ) -> WordHint | None:
        """Get the first hint for a word that the caller has not seen yet."""
        result = await db.execute(
            select(WordHint)
            .where(WordHint.word == word)
            .where(WordHint.id.notin_(not_in or []))
            .order_by(WordHint.hint_order)
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def next_hint_order(self, db: AsyncSession, word: str) -> int:
        """
        The next 1-based hint_order for a word.

        Hints are numbered per word, and the UI renders that number (1⃣2⃣3⃣)
        and keys its list on it, so every hint for a word needs a distinct order.
        """
        result = await db.execute(
            select(func.coalesce(func.max(WordHint.hint_order), 0)).where(WordHint.word == word)
        )
        return result.scalar_one() + 1

    async def create_hint(
        self,
        db: AsyncSession,
        word: str,
        hint_text: str,
        hint_order: int | None = None,
        generated_by: str | None = None,
    ) -> WordHint:
        """Create a new hint for a word, numbering it after the existing ones."""
        if hint_order is None:
            hint_order = await self.next_hint_order(db, word)
        hint = WordHint(
            word=word, hint_text=hint_text, hint_order=hint_order, generated_by=generated_by
        )
        db.add(hint)
        await db.flush()
        await db.refresh(hint)
        return hint

    async def create_user_word_hint(
        self, db: AsyncSession, user_id: UUID, word_hint_id: int, daily_word_id: int
    ) -> UserWordHint:
        """Create a new hint for a user on a specific word."""
        hint = UserWordHint(user_id=user_id, word_hint_id=word_hint_id, daily_word_id=daily_word_id)
        db.add(hint)
        await db.flush()
        await db.refresh(hint)
        return hint


word_hint = CRUDWordHint(WordHint)
