"""allow_multi_specialty_users

Revision ID: c1a2e3f4b5d6
Revises: f2e1921a9b72
Create Date: 2026-08-24 17:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c1a2e3f4b5d6'
down_revision: Union[str, Sequence[str], None] = 'f2e1921a9b72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch_alter_table for SQLite compatibility
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        try:
            batch_op.drop_index('ix_usuarios_username')
        except Exception:
            pass
        batch_op.create_index('ix_usuarios_username', ['username'], unique=False)
        batch_op.create_unique_constraint('uq_usuarios_username_perfil', ['username', 'perfil_id'])


def downgrade() -> None:
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        try:
            batch_op.drop_constraint('uq_usuarios_username_perfil', type_='unique')
        except Exception:
            pass
        try:
            batch_op.drop_index('ix_usuarios_username')
        except Exception:
            pass
        batch_op.create_index('ix_usuarios_username', ['username'], unique=True)
