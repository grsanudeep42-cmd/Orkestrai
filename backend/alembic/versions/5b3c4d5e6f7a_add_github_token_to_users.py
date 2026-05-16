"""Add github_token to users table

Revision ID: 5b3c4d5e6f7a
Revises: 4a2b3c4d5e6f
Create Date: 2026-05-16 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b3c4d5e6f7a'
down_revision: Union[str, None] = '4a2b3c4d5e6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('github_token', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'github_token')
