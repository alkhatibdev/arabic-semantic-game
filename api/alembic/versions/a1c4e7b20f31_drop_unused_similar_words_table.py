"""drop unused similar_words table

The pre-computed-similarity feature never worked: the model declared a
`cosine_similarity` column while the CRUD layer read and wrote
`similarity_score`, so every call raised, and nothing referenced it from any
endpoint. The model, CRUD and precompute script were removed, so the table goes
too rather than lingering as an orphan that `--autogenerate` keeps flagging.

Revision ID: a1c4e7b20f31
Revises: bff757040c8c
Create Date: 2026-11-15

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = 'a1c4e7b20f31'
down_revision: Union[str, Sequence[str], None] = 'bff757040c8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index('ix_similar_words_word_rank', table_name='similar_words')
    op.drop_index(op.f('ix_similar_words_word'), table_name='similar_words')
    op.drop_index(op.f('ix_similar_words_id'), table_name='similar_words')
    op.drop_table('similar_words')


def downgrade() -> None:
    op.create_table(
        'similar_words',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('word', sa.String(), nullable=False),
        sa.Column('similar_word', sa.String(), nullable=False),
        sa.Column('cosine_similarity', sa.Float(), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('word', 'similar_word', name='uq_word_similar_word'),
    )
    op.create_index(op.f('ix_similar_words_id'), 'similar_words', ['id'], unique=False)
    op.create_index(op.f('ix_similar_words_word'), 'similar_words', ['word'], unique=False)
    op.create_index(
        'ix_similar_words_word_rank', 'similar_words', ['word', 'rank'], unique=False
    )
