"""add_started_at_to_schedulings

Revision ID: 7d768a8b929e
Revises: a218349dcd9a
Create Date: 2026-02-06 17:21:26.980557+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "7d768a8b929e"
down_revision: str | None = "a218349dcd9a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration."""
    op.add_column(
        "schedulings",
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Reverte a migration."""
    op.drop_column("schedulings", "started_at")