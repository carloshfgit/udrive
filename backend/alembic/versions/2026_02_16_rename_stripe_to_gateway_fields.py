"""rename_stripe_to_gateway_fields

Revision ID: 4f1e56d7a8b9
Revises: 2eb01092e3e0
Create Date: 2026-02-16 19:15:00.000000+00:00
"""

from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4f1e56d7a8b9"
down_revision: str | None = "2eb01092e3e0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Update Payments table
    op.alter_column('payments', 'stripe_payment_intent_id', new_column_name='gateway_payment_id')
    op.alter_column('payments', 'stripe_transfer_id', new_column_name='gateway_preference_id')
    op.add_column('payments', sa.Column('gateway_provider', sa.String(), nullable=False, server_default='mercadopago'))
    op.add_column('payments', sa.Column('payer_email', sa.String(), nullable=True))

    # 2. Update Transactions table
    op.alter_column('transactions', 'stripe_reference_id', new_column_name='gateway_reference_id')

    # 3. Update Instructor Profiles table
    # stripe_account_id was missing in DB, adding it as deprecated
    op.add_column('instructor_profiles', sa.Column('stripe_account_id', sa.String(length=100), nullable=True))
    op.add_column('instructor_profiles', sa.Column('mp_access_token', sa.Text(), nullable=True))
    op.add_column('instructor_profiles', sa.Column('mp_refresh_token', sa.String(length=100), nullable=True))
    op.add_column('instructor_profiles', sa.Column('mp_token_expiry', sa.DateTime(), nullable=True))
    op.add_column('instructor_profiles', sa.Column('mp_user_id', sa.String(length=50), nullable=True))


def downgrade() -> None:
    # 1. Revert Payments table
    op.drop_column('payments', 'payer_email')
    op.drop_column('payments', 'gateway_provider')
    op.alter_column('payments', 'gateway_preference_id', new_column_name='stripe_transfer_id')
    op.alter_column('payments', 'gateway_payment_id', new_column_name='stripe_payment_intent_id')

    # 2. Revert Transactions table
    op.alter_column('transactions', 'gateway_reference_id', new_column_name='stripe_reference_id')

    # 3. Revert Instructor Profiles table
    op.drop_column('instructor_profiles', 'mp_user_id')
    op.drop_column('instructor_profiles', 'mp_token_expiry')
    op.drop_column('instructor_profiles', 'mp_refresh_token')
    op.drop_column('instructor_profiles', 'mp_access_token')
    op.drop_column('instructor_profiles', 'stripe_account_id')
