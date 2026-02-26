"""adicionar_campos_precificacao_variavel_scheduling

Revision ID: 15e9acc2bb62
Revises: 724ac9b60246
Create Date: 2026-02-26 23:30:18.268281+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "15e9acc2bb62"
down_revision: str | None = "724ac9b60246"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# Definição dos enums
lesson_category_enum = sa.Enum("A", "B", "AB", name="lesson_category_enum")
vehicle_ownership_enum = sa.Enum("instructor", "student", name="vehicle_ownership_enum")


def upgrade() -> None:
    """Adiciona campos de precificação variável à tabela schedulings."""
    # Criar os tipos enum no PostgreSQL
    lesson_category_enum.create(op.get_bind(), checkfirst=True)
    vehicle_ownership_enum.create(op.get_bind(), checkfirst=True)

    # Adicionar colunas à tabela schedulings
    op.add_column(
        "schedulings",
        sa.Column("lesson_category", lesson_category_enum, nullable=True),
    )
    op.add_column(
        "schedulings",
        sa.Column("vehicle_ownership", vehicle_ownership_enum, nullable=True),
    )
    op.add_column(
        "schedulings",
        sa.Column("applied_base_price", sa.Numeric(10, 2), nullable=True),
    )
    op.add_column(
        "schedulings",
        sa.Column("applied_final_price", sa.Numeric(10, 2), nullable=True),
    )


def downgrade() -> None:
    """Remove campos de precificação variável da tabela schedulings."""
    op.drop_column("schedulings", "applied_final_price")
    op.drop_column("schedulings", "applied_base_price")
    op.drop_column("schedulings", "vehicle_ownership")
    op.drop_column("schedulings", "lesson_category")

    # Remover os tipos enum do PostgreSQL
    vehicle_ownership_enum.drop(op.get_bind(), checkfirst=True)
    lesson_category_enum.drop(op.get_bind(), checkfirst=True)
