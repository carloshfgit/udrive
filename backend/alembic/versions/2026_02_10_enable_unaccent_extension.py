"""enable_unaccent_extension

Revision ID: 2b6f242b2b7b
Revises: 2026021001
Create Date: 2026-02-10 19:33:15.378128+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "2b6f242b2b7b"
down_revision: str | None = "2026021001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration."""
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")


def downgrade() -> None:
    """Reverte a migration."""
    op.execute("DROP EXTENSION IF EXISTS unaccent")
