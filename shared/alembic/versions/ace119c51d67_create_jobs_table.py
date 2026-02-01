"""create_jobs_table

Revision ID: ace119c51d67
Revises:
Create Date: 2026-02-01

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'ace119c51d67'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'jobs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('url', sa.String(length=2048), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('company', sa.String(length=255), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('salary', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('extraction_method', sa.String(length=50), nullable=True),
        sa.Column('flagged', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url'),
    )
    op.create_index('ix_jobs_user_id', 'jobs', ['user_id'], unique=False)
    op.create_index('idx_jobs_company', 'jobs', ['company'], unique=False)
    op.create_index('idx_jobs_created_at', 'jobs', ['created_at'], unique=False)
    op.create_index('idx_jobs_flagged', 'jobs', ['flagged'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_jobs_flagged', table_name='jobs')
    op.drop_index('idx_jobs_created_at', table_name='jobs')
    op.drop_index('idx_jobs_company', table_name='jobs')
    op.drop_index('ix_jobs_user_id', table_name='jobs')
    op.drop_table('jobs')
