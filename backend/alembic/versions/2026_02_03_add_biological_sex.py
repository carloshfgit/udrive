"""add_biological_sex_to_users

Revision ID: 7a3b8c9d0e1f
Revises: 2026_02_02_move_personal_info_to_users
Create Date: 2026-02-03 11:43:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "7a3b8c9d0e1f"
down_revision: str = "e3ac9bd9c0ac"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Adiciona coluna biological_sex à tabela users."""
    op.add_column(
        "users",
        sa.Column("biological_sex", sa.String(10), nullable=True),
    )


def downgrade() -> None:
    """Remove coluna biological_sex da tabela users."""
    op.drop_column("users", "biological_sex")
