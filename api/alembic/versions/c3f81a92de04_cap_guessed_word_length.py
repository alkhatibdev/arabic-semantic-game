"""cap guessed_word length

`user_guesses.guessed_word` was an unbounded String, and the API accepted a
guess of any size, so a multi-megabyte value reached both the embedding model
and the table. guessed_word also participates in the uq_user_daily_word_guess
btree index, which Postgres caps at ~2704 bytes per entry, so a long
incompressible guess raised an unhandled database error instead of being
rejected at the boundary.

The API now rejects anything over MAX_GUESS_LENGTH (64); this makes the column
agree. Existing values are truncated to fit - real guesses are a single Arabic
token, so this is a no-op on any genuine row, but the UPDATE runs first so the
ALTER cannot fail on junk that predates the cap.

Revision ID: c3f81a92de04
Revises: a1c4e7b20f31
Create Date: 2026-11-16

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = 'c3f81a92de04'
down_revision: Union[str, Sequence[str], None] = 'a1c4e7b20f31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

MAX_GUESS_LENGTH = 64


def upgrade() -> None:
    # Truncate before narrowing. If two over-long guesses by the same player on
    # the same word share a prefix, this trips uq_user_daily_word_guess and the
    # migration aborts - loudly, and without having altered anything.
    op.execute(
        sa.text(
            "UPDATE user_guesses SET guessed_word = LEFT(guessed_word, :n) "
            "WHERE LENGTH(guessed_word) > :n"
        ).bindparams(n=MAX_GUESS_LENGTH)
    )
    op.alter_column(
        'user_guesses',
        'guessed_word',
        existing_type=sa.String(),
        type_=sa.String(length=MAX_GUESS_LENGTH),
        existing_nullable=False,
    )


def downgrade() -> None:
    # Widening back is lossless; the truncation above is not reversible.
    op.alter_column(
        'user_guesses',
        'guessed_word',
        existing_type=sa.String(length=MAX_GUESS_LENGTH),
        type_=sa.String(),
        existing_nullable=False,
    )
