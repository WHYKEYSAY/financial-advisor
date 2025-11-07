"""Add VCM fields to cards table

Revision ID: abc123def456
Revises: 6f2461c1a24d
Create Date: 2025-11-07 05:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'abc123def456'
down_revision: Union[str, None] = '6f2461c1a24d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add VCM (Virtual Credit Manager) fields to cards table
    op.add_column('cards', sa.Column('current_balance', sa.Numeric(precision=10, scale=2), server_default='0', nullable=True))
    op.add_column('cards', sa.Column('vcm_enabled', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('cards', sa.Column('vcm_priority', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Remove VCM fields from cards table
    op.drop_column('cards', 'vcm_priority')
    op.drop_column('cards', 'vcm_enabled')
    op.drop_column('cards', 'current_balance')
