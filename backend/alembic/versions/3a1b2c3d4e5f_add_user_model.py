"""Add user model and link to project

Revision ID: 3a1b2c3d4e5f
Revises: 235b877c62c1
Create Date: 2026-05-16 10:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a1b2c3d4e5f'
down_revision: Union[str, None] = '235b877c62c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create users table
    op.create_table('users',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    
    # 2. Add user_id to projects
    # For existing projects, we'll allow nullable for now or delete them
    # Since the user wants to delete all data, we can just wipe tables in this migration
    op.execute("DELETE FROM generated_artifacts")
    op.execute("DELETE FROM agent_logs")
    op.execute("DELETE FROM projects")
    
    op.add_column('projects', sa.Column('user_id', sa.String(length=36), nullable=True))
    op.create_foreign_key('fk_projects_user_id', 'projects', 'users', ['user_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    op.drop_constraint('fk_projects_user_id', 'projects', type_='foreignkey')
    op.drop_column('projects', 'user_id')
    op.drop_table('users')
