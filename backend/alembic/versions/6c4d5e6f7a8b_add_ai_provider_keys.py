"""Add AI provider keys to user table

Revision ID: 6c4d5e6f7a8b
Revises: 5b3c4d5e6f7a
Create Date: 2026-05-17 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c4d5e6f7a8b'
down_revision: Union[str, None] = '5b3c4d5e6f7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('openai_key', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('gemini_key', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('groq_key', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('openrouter_key', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'openrouter_key')
    op.drop_column('users', 'groq_key')
    op.drop_column('users', 'gemini_key')
    op.drop_column('users', 'openai_key')
