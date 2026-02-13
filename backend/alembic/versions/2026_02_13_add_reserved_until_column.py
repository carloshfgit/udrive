"""add_reserved_until_column

Revision ID: 76c637bb52ab
Revises: 9297b49f0576
Create Date: 2026-02-13 14:33:29.876236+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "76c637bb52ab"
down_revision: str | None = "9297b49f0576"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration."""
    # 1. Adicionar coluna reserved_until à tabela schedulings
    op.add_column(
        "schedulings",
        sa.Column("reserved_until", sa.DateTime(timezone=True), nullable=True),
    )

    # 2. Índice parcial para busca rápida de reservas expiradas
    # Agora o valor 'reserved' já foi comitado e pode ser usado.
    op.create_index(
        "ix_schedulings_reserved_until",
        "schedulings",
        ["reserved_until"],
        postgresql_where=sa.text("status = 'reserved'"),
    )


def downgrade() -> None:
    """Reverte a migration."""
    op.drop_index("ix_schedulings_reserved_until", table_name="schedulings")
    op.drop_column("schedulings", "reserved_until")
