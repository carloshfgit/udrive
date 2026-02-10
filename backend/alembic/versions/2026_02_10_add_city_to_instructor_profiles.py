"""add_city_to_instructor_profiles

Revision ID: 2026021001
Revises: b9c8d7e6a5f4
Create Date: 2026-02-10 14:45:00.000000+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2026021001"
down_revision: str | None = "51b916bdfa24"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration."""
    op.add_column(
        "instructor_profiles",
        sa.Column("city", sa.String(255), nullable=True),
    )
    
    # Índice para buscas por cidade
    op.create_index(
        "ix_instructor_profiles_city",
        "instructor_profiles",
        ["city"],
    )


def downgrade() -> None:
    """Reverte a migration."""
    op.drop_index("ix_instructor_profiles_city", table_name="instructor_profiles")
    op.drop_column("instructor_profiles", "city")
