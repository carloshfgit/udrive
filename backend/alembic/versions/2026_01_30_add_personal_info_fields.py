"""Add phone cpf birthdate to student profiles

Revision ID: add_personal_info_fields
Revises: fd14a3a54326
Create Date: 2026-01-30 10:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_personal_info_fields'
down_revision = 'fd14a3a54326'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add phone, cpf, and birth_date columns to student_profiles table."""
    op.add_column(
        'student_profiles',
        sa.Column('phone', sa.String(20), nullable=False, server_default='')
    )
    op.add_column(
        'student_profiles',
        sa.Column('cpf', sa.String(14), nullable=False, server_default='')
    )
    op.add_column(
        'student_profiles',
        sa.Column('birth_date', sa.Date(), nullable=True)
    )


def downgrade() -> None:
    """Remove phone, cpf, and birth_date columns from student_profiles table."""
    op.drop_column('student_profiles', 'birth_date')
    op.drop_column('student_profiles', 'cpf')
    op.drop_column('student_profiles', 'phone')
