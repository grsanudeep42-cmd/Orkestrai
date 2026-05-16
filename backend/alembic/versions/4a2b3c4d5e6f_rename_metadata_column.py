"""Rename metadata to agent_metadata

Revision ID: 4a2b3c4d5e6f
Revises: 3a1b2c3d4e5f
Create Date: 2026-05-16 11:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a2b3c4d5e6f'
down_revision: Union[str, None] = '3a1b2c3d4e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename column in agent_logs table
    op.alter_column('agent_logs', 'metadata', new_column_name='agent_metadata')


def downgrade() -> None:
    # Rename column back if needed
    op.alter_column('agent_logs', 'agent_metadata', new_column_name='metadata')
