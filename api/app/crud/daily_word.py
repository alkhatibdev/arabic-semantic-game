"""CRUD operations for DailyWord model."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.daily_word import DailyWord


class CRUDDailyWord(CRUDBase[DailyWord, DailyWord, DailyWord]):
    """CRUD operations for DailyWord model."""

    async def get_by_date(self, db: AsyncSession, challenge_date: date) -> DailyWord | None:
        """Get daily word by date."""
        result = await db.execute(select(DailyWord).where(DailyWord.date == challenge_date))
        return result.scalar_one_or_none()

    async def get_game_number(self, db: AsyncSession, challenge_date: date) -> int:
        """
        Get the 1-based position of a date among all challenges.

        Counted in SQL rather than by fetching every date, which the previous
        implementation did on each request.
        """
        result = await db.execute(
            select(func.count(DailyWord.id)).where(DailyWord.date <= challenge_date)
        )
        return result.scalar_one()

    async def create_daily_word(
        self, db: AsyncSession, word: str, challenge_date: date
    ) -> DailyWord:
        """Create a new daily word challenge."""
        daily_word = DailyWord(word=word, date=challenge_date)
        db.add(daily_word)
        await db.flush()
        await db.refresh(daily_word)
        return daily_word


daily_word = CRUDDailyWord(DailyWord)
