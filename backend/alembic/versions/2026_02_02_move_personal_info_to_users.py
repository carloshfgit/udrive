"""move_personal_info_to_users

Revision ID: e3ac9bd9c0ac
Revises: add_personal_info_fields
Create Date: 2026-02-02 12:43:19.441484+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3ac9bd9c0ac'
down_revision: Union[str, None] = 'add_personal_info_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns to users table
    op.add_column('users', sa.Column('phone', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('cpf', sa.String(length=14), nullable=True))
    op.add_column('users', sa.Column('birth_date', sa.Date(), nullable=True))

    # Drop columns from student_profiles
    op.drop_column('student_profiles', 'phone')
    op.drop_column('student_profiles', 'cpf')
    op.drop_column('student_profiles', 'birth_date')


def downgrade() -> None:
    # Add columns back to student_profiles
    op.add_column('student_profiles', sa.Column('birth_date', sa.Date(), autoincrement=False, nullable=True))
    op.add_column('student_profiles', sa.Column('cpf', sa.String(length=14), server_default=sa.text("''::character varying"), autoincrement=False, nullable=False))
    op.add_column('student_profiles', sa.Column('phone', sa.String(length=20), server_default=sa.text("''::character varying"), autoincrement=False, nullable=False))

    # Drop columns from users
    op.drop_column('users', 'birth_date')
    op.drop_column('users', 'cpf')
    op.drop_column('users', 'phone')
