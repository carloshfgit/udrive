"""add_student_confirmed_at

Revision ID: 51b916bdfa24
Revises: b9c8d7e6a5f4
Create Date: 2026-02-09 21:19:27.217962+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "51b916bdfa24"
down_revision: str | None = "b9c8d7e6a5f4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration."""
    op.add_column(
        "schedulings",
        sa.Column("student_confirmed_at", sa.DateTime(timezone=True), nullable=True),
    )
def downgrade() -> None:
    """Reverte a migration."""
    op.drop_column("schedulings", "student_confirmed_at")
