"""add_payment_tables

Revision ID: fd14a3a54326
Revises: e27f6f8202c3
Create Date: 2026-01-29 18:24:21.115751+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "fd14a3a54326"
down_revision: str | None = "e27f6f8202c3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration."""
    pass


def downgrade() -> None:
    """Reverte a migration."""
    pass
