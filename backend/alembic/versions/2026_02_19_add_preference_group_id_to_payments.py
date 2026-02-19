"""add_preference_group_id_to_payments

Revision ID: 3aa10a10c884
Revises: 5f2e67d8a9c0
Create Date: 2026-02-19 02:11:36.061988+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "3aa10a10c884"
down_revision: str | None = "5f2e67d8a9c0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration."""
    op.add_column("payments", sa.Column("preference_group_id", sa.UUID(), nullable=True))
    op.create_index(
        op.f("ix_payments_preference_group_id"),
        "payments",
        ["preference_group_id"],
        unique=False,
    )


def downgrade() -> None:
    """Reverte a migration."""
    op.drop_index(op.f("ix_payments_preference_group_id"), table_name="payments")
    op.drop_column("payments", "preference_group_id")