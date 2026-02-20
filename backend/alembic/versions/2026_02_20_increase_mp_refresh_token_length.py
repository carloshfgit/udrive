"""increase mp_refresh_token length

Revision ID: 3d10179d9390
Revises: 3aa10a10c884
Create Date: 2026-02-20 14:51:01.400912+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "3d10179d9390"
down_revision: str | None = "3aa10a10c884"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration."""
    op.alter_column(
        "instructor_profiles",
        "mp_refresh_token",
        type_=sa.Text(),
        existing_type=sa.String(length=100),
    )


def downgrade() -> None:
    """Reverte a migration."""
    op.alter_column(
        "instructor_profiles",
        "mp_refresh_token",
        type_=sa.String(length=100),
        existing_type=sa.Text(),
    )