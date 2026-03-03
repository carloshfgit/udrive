"""add_disputed_status_to_scheduling_enum

Revision ID: 8a3c1f5d2b7e
Revises: 4222a096fadc
Create Date: 2026-03-03 13:45:00.000000+00:00
"""

from collections.abc import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "8a3c1f5d2b7e"
down_revision: str | None = "4222a096fadc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Adiciona o valor 'disputed' ao enum scheduling_status_enum."""
    op.execute("ALTER TYPE scheduling_status_enum ADD VALUE IF NOT EXISTS 'disputed'")


def downgrade() -> None:
    """
    Remove o valor 'disputed' do enum.
    
    Nota: PostgreSQL não suporta remoção direta de valores de enum.
    Em produção, seria necessário recriar o enum sem o valor.
    Para simplificar, apenas logamos um aviso.
    """
    # PostgreSQL não permite DROP VALUE de enum diretamente.
    # Se necessário reverter, recriar o enum manualmente.
    pass
