"""Game logic service."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.daily_word import daily_word as crud_daily_word
from app.crud.guess import user_guess as crud_user_guess
from app.crud.user import user as crud_user
from app.schemas.game import GameStatusResponse
from app.schemas.guess import GuessResponse
from app.services.similarity_service import similarity_service


class GameService:
    """Service for game logic and operations."""

    async def submit_guess(
        self,
        db: AsyncSession,
        user_id: UUID,
        challenge_date,
        guessed_word: str,
        is_given_up: bool = False,
    ) -> GuessResponse:
        """
        Submit a guess for a daily challenge.

        Args:
            db: Database session
            user_id: User UUID
            challenge_date: Challenge date
            guessed_word: The word guessed by the user
            is_given_up: True if the user gave up on the challenge

        Returns:
            GuessResponse with similarity scores and correctness
        """
        # Ensure user exists
        await crud_user.get_or_create(db, user_id)

        # Get daily word
        daily_word = await crud_daily_word.get_by_date(db, challenge_date)
        if not daily_word:
            raise ValueError(f"No challenge found for date {challenge_date}")

        target_word = daily_word.word.strip()
        guessed_word = target_word if is_given_up else guessed_word.strip()

        # Check if word is correct
        is_correct = guessed_word == target_word

        # Calculate similarity (off the event loop - encode() is CPU-bound)
        similarity_score, cosine_sim = await similarity_service.calculate_similarity_async(
            target_word, guessed_word
        )

        # Check if guess is submitted by the same user
        guess = await crud_user_guess.get_user_guess_by_user_id_and_daily_word_id_and_guessed_word(
            db, user_id, daily_word.id, guessed_word
        )

        if not guess:
            # Create the guess
            guess = await crud_user_guess.create_guess(
                db=db,
                user_id=user_id,
                daily_word_id=daily_word.id,
                guessed_word=guessed_word,
                similarity_score=similarity_score,
                cosine_similarity=cosine_sim,
                is_correct=is_correct,
                is_given_up=is_given_up,
            )

        # Get attempt number dynamically
        attempts = await crud_user_guess.count_attempts(db, user_id, daily_word.id)

        # Create response
        return GuessResponse(
            id=guess.id,
            word=guess.guessed_word,
            similarity_score=guess.similarity_score,
            cosine_similarity=guess.cosine_similarity,
            is_correct=guess.is_correct,
            attempt_number=attempts,
            created_at=guess.created_at,
            is_given_up=bool(guess.is_given_up),
        )

    async def get_game_status(
        self,
        db: AsyncSession,
        user_id: UUID,
        challenge_date,
    ) -> GameStatusResponse:
        """
        Get the game status for a user on a specific date.

        Args:
            db: Database session
            user_id: User UUID
            challenge_date: Challenge date

        Returns:
            GameStatusResponse with won status, attempts, and target word (if won)
        """
        # Get daily word
        daily_word = await crud_daily_word.get_by_date(db, challenge_date)
        if not daily_word:
            raise ValueError(f"No challenge found for date {challenge_date}")

        # Check if user has won
        has_won = await crud_user_guess.has_won(db, user_id, daily_word.id)

        # Get attempt count
        attempts = await crud_user_guess.count_attempts(db, user_id, daily_word.id)

        # Get winning guess if won
        won_at = None
        target_word = None
        if has_won:
            winning_guess = await crud_user_guess.get_winning_guess(db, user_id, daily_word.id)
            if winning_guess:
                won_at = winning_guess.created_at
                target_word = daily_word.word

        return GameStatusResponse(
            won=has_won,
            attempts=attempts,
            won_at=won_at,
            target_word=target_word,
        )

    async def get_user_guesses_with_attempts(
        self,
        db: AsyncSession,
        user_id: UUID,
        challenge_date,
    ) -> list[GuessResponse]:
        """
        Get all guesses for a user with attempt numbers.

        Args:
            db: Database session
            user_id: User UUID
            challenge_date: Challenge date

        Returns:
            List of GuessResponse with attempt numbers
        """
        # Get daily word
        daily_word = await crud_daily_word.get_by_date(db, challenge_date)
        if not daily_word:
            return []

        # Get all guesses
        guesses = await crud_user_guess.get_user_guesses(db, user_id, daily_word.id)

        # Convert to responses with attempt numbers
        guess_responses = []
        for idx, guess in enumerate(guesses, start=1):
            guess_responses.append(
                GuessResponse(
                    id=guess.id,
                    word=guess.guessed_word,
                    similarity_score=guess.similarity_score,
                    cosine_similarity=guess.cosine_similarity,
                    is_correct=guess.is_correct,
                    attempt_number=idx,
                    created_at=guess.created_at,
                    is_given_up=bool(guess.is_given_up),
                )
            )

        return guess_responses


# Global game service instance
game_service = GameService()
