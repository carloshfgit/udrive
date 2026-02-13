"""add_reserved_until_and_reserved_status

Revision ID: 9297b49f0576
Revises: 2026_02_13_add_escrow_support
Create Date: 2026-02-13 14:25:17.922061+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "9297b49f0576"
down_revision: str | None = "2026_02_13_add_escrow_support"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration."""
    # 1. Adicionar valor 'reserved' ao enum scheduling_status_enum
    # PostgreSQL não suporta usar o novo valor na mesma transação.
    # Por isso, apenas adicionamos o valor aqui e criaremos a coluna em outro arquivo.
    op.execute("ALTER TYPE scheduling_status_enum ADD VALUE IF NOT EXISTS 'reserved'")


def downgrade() -> None:
    """Reverte a migration."""
    # Nota: PostgreSQL não suporta remoção de valores de enum.
    # O valor 'reserved' permanecerá no enum após downgrade.
    pass