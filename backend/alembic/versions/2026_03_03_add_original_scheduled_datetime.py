"""add_original_scheduled_datetime

Revision ID: 9b4d2g6e3c8f
Revises: 8a3c1f5d2b7e
Create Date: 2026-03-03 14:42:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "9b4d2g6e3c8f"
down_revision: str | None = "8a3c1f5d2b7e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Adiciona coluna para preservar data original em reagendamentos dentro da janela de multa."""
    op.add_column(
        "schedulings",
        sa.Column(
            "original_scheduled_datetime",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Data original preservada para trava de reembolso em reagendamentos dentro da janela de multa",
        ),
    )


def downgrade() -> None:
    """Remove coluna original_scheduled_datetime."""
    op.drop_column("schedulings", "original_scheduled_datetime")
