"""Hint-related services."""

import logging
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud.user import user as crud_user
from app.crud.word_hint import word_hint as crud_word_hint
from app.models.daily_word import DailyWord
from app.models.word_hint import WordHint
from app.schemas.general import BasicResponse
from app.schemas.word_hint import WordHintsRequest

logger = logging.getLogger(__name__)


class HintService:
    """Service for hint-related operations."""

    async def set_hints(self, db: AsyncSession, request: WordHintsRequest) -> BasicResponse:
        """Set hints for a word, skipping texts that already exist."""
        current = await crud_word_hint.get_hints_for_word(db=db, word=request.word)
        existing = {h.hint_text for h in current}
        next_order = max((h.hint_order for h in current), default=0) + 1

        created = 0
        for hint in request.hints:
            text = hint.strip()
            if not text or text in existing:
                continue
            await crud_word_hint.create_hint(
                db=db, word=request.word, hint_text=text, hint_order=next_order
            )
            existing.add(text)
            next_order += 1
            created += 1

        return BasicResponse(success=True, message=f"Created {created} hint(s)")

    async def get_user_provided_hints(
        self, db: AsyncSession, user_id: UUID, word: str
    ) -> list[WordHint]:
        """Get the hints already revealed to a user for a word."""
        return await crud_word_hint.get_word_hints_for_user(db=db, user_id=user_id, word=word)

    async def get_hints_for_word(self, db: AsyncSession, word: str) -> list[str]:
        """Get all hint texts for a word."""
        hints = await crud_word_hint.get_hints_for_word(db=db, word=word)
        return [h.hint_text for h in hints]

    async def provide_hint(
        self, db: AsyncSession, user_id: UUID, daily_word: DailyWord
    ) -> WordHint:
        """Reveal the next unseen hint for a user on a specific word."""
        await crud_user.get_or_create(db, user_id)

        seen = await self.get_user_provided_hints(db=db, user_id=user_id, word=daily_word.word)
        if len(seen) >= settings.MAX_HINTS_PER_USER:
            raise HTTPException(
                status_code=403, detail="You have already used all hints for this word"
            )

        hint = await crud_word_hint.get_new_hint(
            db=db, word=daily_word.word, not_in=[h.id for h in seen]
        )
        if not hint:
            logger.info("No hints available for word id=%s", daily_word.id)
            raise HTTPException(status_code=404, detail="No hints available for this word")

        await crud_word_hint.create_user_word_hint(
            db=db, user_id=user_id, word_hint_id=hint.id, daily_word_id=daily_word.id
        )
        return hint


# Global hint service instance
hint_service = HintService()
