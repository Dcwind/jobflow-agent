"""add_stage_column

Revision ID: aaea80e1b6e8
Revises: ace119c51d67
Create Date: 2026-02-01 08:59:40.415024

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aaea80e1b6e8'
down_revision: Union[str, Sequence[str], None] = 'ace119c51d67'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column("stage", sa.String(20), nullable=False, server_default="Backlog"),
    )


def downgrade() -> None:
    op.drop_column("jobs", "stage")
