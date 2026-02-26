"""add_pricing_columns_to_instructor_profiles

Revision ID: 724ac9b60246
Revises: 53a1473d67bb
Create Date: 2026-02-26 21:39:02.814957+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "724ac9b60246"
down_revision: str | None = "53a1473d67bb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Adiciona colunas de preço por categoria e tipo de veículo."""
    op.add_column(
        "instructor_profiles",
        sa.Column("price_cat_a_instructor_vehicle", sa.Numeric(10, 2), nullable=True),
    )
    op.add_column(
        "instructor_profiles",
        sa.Column("price_cat_a_student_vehicle", sa.Numeric(10, 2), nullable=True),
    )
    op.add_column(
        "instructor_profiles",
        sa.Column("price_cat_b_instructor_vehicle", sa.Numeric(10, 2), nullable=True),
    )
    op.add_column(
        "instructor_profiles",
        sa.Column("price_cat_b_student_vehicle", sa.Numeric(10, 2), nullable=True),
    )


def downgrade() -> None:
    """Reverte a migration."""
    op.drop_column("instructor_profiles", "price_cat_a_instructor_vehicle")
    op.drop_column("instructor_profiles", "price_cat_a_student_vehicle")
    op.drop_column("instructor_profiles", "price_cat_b_instructor_vehicle")
    op.drop_column("instructor_profiles", "price_cat_b_student_vehicle")
