"""add_rescheduled_by_to_schedulings

Revision ID: 2eb01092e3e0
Revises: 2b6f242b2b7b
Create Date: 2026-02-11 16:29:56.141727+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "2eb01092e3e0"
down_revision: str | None = "2b6f242b2b7b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration."""
    op.add_column(
        "schedulings",
        sa.Column("rescheduled_by", sa.UUID(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )


def downgrade() -> None:
    """Reverte a migration."""
    op.drop_column("schedulings", "rescheduled_by")
