"""Add HELD/DISPUTED payment statuses and transfer_group column

Revision ID: 2026_02_13_add_escrow_support
Revises: 2026_02_13_add_payment_pricing_and_refund_fields
Create Date: 2026-02-13 10:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2026_02_13_add_escrow_support'
down_revision: str = '4f43612ea0c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Adicionar novos valores ao enum paymentstatus
    # PostgreSQL requer ALTER TYPE para adicionar valores a um enum existente
    op.execute("ALTER TYPE paymentstatus ADD VALUE IF NOT EXISTS 'held'")
    op.execute("ALTER TYPE paymentstatus ADD VALUE IF NOT EXISTS 'disputed'")

    # 2. Adicionar coluna transfer_group à tabela payments
    op.add_column(
        'payments',
        sa.Column('transfer_group', sa.String(), nullable=True)
    )


def downgrade() -> None:
    # 1. Remover coluna transfer_group
    op.drop_column('payments', 'transfer_group')

    # NOTA: PostgreSQL não suporta remoção de valores de enum diretamente.
    # Para fazer rollback completo, seria necessário:
    #   1. Criar novo tipo enum sem os valores
    #   2. Alterar a coluna para usar o novo tipo
    #   3. Remover o tipo antigo
    # Como isso é complexo e raramente necessário, apenas logamos o aviso.
    # Os valores 'held' e 'disputed' permanecerão no enum.
