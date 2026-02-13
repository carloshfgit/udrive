"""add_reschedule_count_and_disputed_status

Revision ID: 645b36ce3121
Revises: 76c637bb52ab
Create Date: 2026-02-13 14:48:42.224170+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "645b36ce3121"
down_revision: str | None = "76c637bb52ab"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration."""
    # 1. Adicionar coluna reschedule_count
    op.add_column(
        "schedulings",
        sa.Column("reschedule_count", sa.Integer(), nullable=False, server_default="0"),
    )

    # 2. Adicionar valor 'disputed' ao enum scheduling_status_enum
    # NOTA: PostgreSQL não permite ALTER TYPE ADD VALUE dentro de transação em algumas versões.
    # Mas como o Alembic roda em transação por padrão, usamos execute().
    op.execute("ALTER TYPE scheduling_status_enum ADD VALUE 'disputed'")


def downgrade() -> None:
    """Reverte a migration."""
    # 1. Remover coluna reschedule_count
    op.drop_column("schedulings", "reschedule_count")

    # 2. Nota: Enums do Postgres não suportam remoção de valores facilmente.
    # Seguindo DB_VISION.md, não tentamos remover o valor do enum no downgrade
    # para evitar problemas de integridade ou complexidade excessiva.
    pass