"""ajustar_colunas_disputes

Revision ID: 804229d529e4
Revises: 295387644590
Create Date: 2026-03-05 18:12:14.443489+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "804229d529e4"
down_revision: str | None = "295387644590"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Renomear admin_notes para resolution_notes
    op.alter_column('disputes', 'admin_notes', new_column_name='resolution_notes')
    
    # 2. Adicionar refund_type (vai ser usado para full/partial refund)
    op.add_column('disputes', sa.Column('refund_type', sa.String(length=10), nullable=True))
def downgrade() -> None:
    # Reverter as alterações
    op.drop_column('disputes', 'refund_type')
    op.alter_column('disputes', 'resolution_notes', new_column_name='admin_notes')
