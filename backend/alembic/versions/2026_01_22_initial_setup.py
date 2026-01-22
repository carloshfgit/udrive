"""
Initial Setup - Enable PostGIS Extension

Revision ID: 0001
Revises: None
Create Date: 2026-01-22
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial_setup"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Aplica a migration inicial.

    - Habilita extensão PostGIS
    - Habilita extensão uuid-ossp para UUIDs
    """
    # Habilitar extensão PostGIS para suporte a geometria
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # Habilitar extensão uuid-ossp para geração de UUIDs
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')


def downgrade() -> None:
    """
    Reverte a migration inicial.

    Nota: Remover extensões pode afetar outros objetos do banco.
    Use com cuidado em produção.
    """
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
    op.execute("DROP EXTENSION IF EXISTS postgis CASCADE")
