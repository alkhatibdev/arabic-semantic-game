"""Game and guess-related endpoints."""

from datetime import date as date_type
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import settings
from app.core.rate_limiter import RateLimiter
from app.crud.daily_word import daily_word as crud_daily_word
from app.schemas.game import GameStateResponse, GameStatusResponse
from app.schemas.guess import GiveUpRequest, GuessRequest, GuessResponse
from app.schemas.word_hint import WordHintResponse
from app.services.game_service import game_service
from app.services.hint_service import hint_service

router = APIRouter()


def _parse_past_date(challenge_date: str) -> date_type:
    """Parse a YYYY-MM-DD path segment and reject anything in the future."""
    try:
        parsed = date_type.fromisoformat(challenge_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD") from None

    if parsed > date_type.today():
        raise HTTPException(status_code=403, detail="Cannot access future challenges")
    return parsed


@router.post(
    "/guess",
    response_model=GuessResponse,
    dependencies=[Depends(RateLimiter(times=30, seconds=60))],
)
async def submit_guess(guess_request: GuessRequest, db: AsyncSession = Depends(get_db)):
    """Submit a guess and calculate its similarity to the target word."""
    if guess_request.challenge_date > date_type.today():
        raise HTTPException(status_code=403, detail="Cannot submit guesses for future challenges")

    if not guess_request.word.strip():
        raise HTTPException(status_code=400, detail="Word cannot be empty")

    try:
        return await game_service.submit_guess(
            db=db,
            user_id=guess_request.user_id,
            challenge_date=guess_request.challenge_date,
            guessed_word=guess_request.word.strip(),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post(
    "/giveup",
    response_model=GuessResponse,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def give_up(give_up_request: GiveUpRequest, db: AsyncSession = Depends(get_db)):
    """Give up on a challenge, revealing the target word."""
    if give_up_request.challenge_date > date_type.today():
        raise HTTPException(status_code=403, detail="Cannot give up on future challenges")

    try:
        return await game_service.submit_guess(
            db=db,
            user_id=give_up_request.user_id,
            challenge_date=give_up_request.challenge_date,
            guessed_word="",
            is_given_up=True,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get(
    "/{challenge_date}/guesses/{user_id}",
    response_model=list[GuessResponse],
    dependencies=[Depends(RateLimiter(times=30, seconds=60))],
)
async def get_guesses(
    challenge_date: str,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get all guesses for a user on a specific date."""
    parsed_date = _parse_past_date(challenge_date)
    return await game_service.get_user_guesses_with_attempts(
        db=db, user_id=user_id, challenge_date=parsed_date
    )


@router.get(
    "/{challenge_date}/status/{user_id}",
    response_model=GameStatusResponse,
    dependencies=[Depends(RateLimiter(times=30, seconds=60))],
)
async def get_game_status(
    challenge_date: str,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get game status for a user on a specific date."""
    parsed_date = _parse_past_date(challenge_date)

    try:
        return await game_service.get_game_status(
            db=db, user_id=user_id, challenge_date=parsed_date
        )
    except ValueError as e:
        # No challenge exists for that date - say so, rather than returning a
        # 200 that looks like a fresh game.
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get(
    "/{challenge_date}/state/{user_id}",
    response_model=GameStateResponse,
    dependencies=[Depends(RateLimiter(times=30, seconds=60))],
)
async def get_game_state(
    challenge_date: str,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get complete game state: guesses, status and revealed hints."""
    parsed_date = _parse_past_date(challenge_date)

    daily_word = await crud_daily_word.get_by_date(db, parsed_date)
    if not daily_word:
        raise HTTPException(status_code=404, detail="Challenge not found for this date")

    game_number = await crud_daily_word.get_game_number(db, parsed_date)

    guesses = await game_service.get_user_guesses_with_attempts(
        db=db, user_id=user_id, challenge_date=parsed_date
    )

    status = await game_service.get_game_status(db=db, user_id=user_id, challenge_date=parsed_date)

    hints = await hint_service.get_user_provided_hints(db=db, user_id=user_id, word=daily_word.word)

    return GameStateResponse(
        challenge_date=parsed_date,
        game_number=game_number,
        guesses=guesses,
        game_status=status,
        has_won=status.won,
        hints=[WordHintResponse(hint_text=h.hint_text, hint_order=h.hint_order) for h in hints],
        max_hints=settings.MAX_HINTS_PER_USER,
    )


@router.get(
    "/{challenge_date}/hints/{user_id}",
    response_model=list[WordHintResponse],
    dependencies=[Depends(RateLimiter(times=60, seconds=60))],
)
async def get_hints(
    challenge_date: str,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get the hints already revealed to a user for a specific date."""
    parsed_date = _parse_past_date(challenge_date)

    daily_word = await crud_daily_word.get_by_date(db, parsed_date)
    if not daily_word:
        raise HTTPException(status_code=404, detail="Challenge not found for this date")

    hints = await hint_service.get_user_provided_hints(db=db, user_id=user_id, word=daily_word.word)
    return [WordHintResponse(hint_text=h.hint_text, hint_order=h.hint_order) for h in hints]


@router.post(
    "/{challenge_date}/hints/{user_id}",
    response_model=WordHintResponse,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def provide_hint(
    challenge_date: str,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Reveal the next hint for a user on a specific date."""
    parsed_date = _parse_past_date(challenge_date)

    daily_word = await crud_daily_word.get_by_date(db, parsed_date)
    if not daily_word:
        raise HTTPException(status_code=404, detail="Challenge not found for this date")

    hint = await hint_service.provide_hint(db=db, user_id=user_id, daily_word=daily_word)
    return WordHintResponse(hint_text=hint.hint_text, hint_order=hint.hint_order)
