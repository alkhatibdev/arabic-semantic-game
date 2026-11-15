"""Challenge-related endpoints."""

from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.rate_limiter import RateLimiter
from app.crud.daily_word import daily_word as crud_daily_word
from app.schemas.challenge import ChallengeResponse

router = APIRouter()


@router.get(
    "/{challenge_date}",
    response_model=ChallengeResponse,
    dependencies=[Depends(RateLimiter(times=60, seconds=60))],
)
async def get_challenge(challenge_date: str, db: AsyncSession = Depends(get_db)):
    """
    Get challenge for a specific date.

    Args:
        challenge_date: Date in YYYY-MM-DD format, or "today"
    """
    today = date_type.today()

    if challenge_date == "today":
        parsed_date = today
    else:
        try:
            parsed_date = date_type.fromisoformat(challenge_date)
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
            ) from None

    # Never reveal that a future challenge exists.
    if parsed_date > today:
        raise HTTPException(status_code=403, detail="Cannot access future challenges")

    daily_word = await crud_daily_word.get_by_date(db, parsed_date)
    if not daily_word:
        return ChallengeResponse(date=parsed_date, game_number=0, has_challenge=False)

    game_number = await crud_daily_word.get_game_number(db, parsed_date)

    return ChallengeResponse(
        date=parsed_date,
        game_number=game_number,
        has_challenge=True,
    )
