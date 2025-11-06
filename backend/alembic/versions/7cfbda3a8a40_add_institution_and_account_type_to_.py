"""add_institution_and_account_type_to_statement

Revision ID: 7cfbda3a8a40
Revises: e9a3b3c92ae9
Create Date: 2025-11-06 02:49:05.470777

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7cfbda3a8a40'
down_revision: Union[str, None] = 'e9a3b3c92ae9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add institution column (e.g., 'CIBC', 'RBC', 'MBNA', 'PC Financial')
    op.add_column('statements', sa.Column('institution', sa.String(100), nullable=True))
    
    # Add account_type column ('credit_card', 'checking', 'savings')
    op.add_column('statements', sa.Column('account_type', sa.String(50), nullable=True))
    
    # Add account_number/card_number (last 4 digits or masked)
    op.add_column('statements', sa.Column('account_number', sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column('statements', 'account_number')
    op.drop_column('statements', 'account_type')
    op.drop_column('statements', 'institution')
