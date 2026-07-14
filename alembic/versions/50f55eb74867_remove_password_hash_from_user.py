"""remove_password_hash_from_user

Revision ID: 50f55eb74867
Revises: 4b0061422399
Create Date: 2026-07-14 13:49:02.168054

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50f55eb74867'
down_revision: Union[str, Sequence[str], None] = '4b0061422399'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('usuarios') as batch_op:
        batch_op.drop_column('password_hash')


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('usuarios') as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.String(), nullable=False, server_default=''))
