"""add_categorizacoes_profissionais

Revision ID: d2e3f4a5b6c7
Revises: c1a2e3f4b5d6
Create Date: 2026-09-02 12:46:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd2e3f4a5b6c7'
down_revision: Union[str, Sequence[str], None] = 'c1a2e3f4b5d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Cria tabela categorizacoes_profissionais
    op.create_table(
        'categorizacoes_profissionais',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('medico', sa.String(), nullable=False),
        sa.Column('especialidade', sa.String(), nullable=False),
        sa.Column('categorias_json', sa.Text(), nullable=False, server_default='[]'),
        sa.UniqueConstraint('medico', 'especialidade', name='uq_categorizacao_medico_especialidade')
    )
    op.create_index('ix_categorizacoes_profissionais_id', 'categorizacoes_profissionais', ['id'], unique=False)
    op.create_index('ix_categorizacoes_profissionais_medico', 'categorizacoes_profissionais', ['medico'], unique=False)
    op.create_index('ix_categorizacoes_profissionais_especialidade', 'categorizacoes_profissionais', ['especialidade'], unique=False)

    # 2. Adiciona coluna categorizacao em solicitacoes
    with op.batch_alter_table('solicitacoes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('categorizacao', sa.String(), nullable=True))

    # 3. Adiciona coluna categorizacao em pacientes
    with op.batch_alter_table('pacientes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('categorizacao', sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('pacientes', schema=None) as batch_op:
        batch_op.drop_column('categorizacao')

    with op.batch_alter_table('solicitacoes', schema=None) as batch_op:
        batch_op.drop_column('categorizacao')

    op.drop_index('ix_categorizacoes_profissionais_especialidade', table_name='categorizacoes_profissionais')
    op.drop_index('ix_categorizacoes_profissionais_medico', table_name='categorizacoes_profissionais')
    op.drop_index('ix_categorizacoes_profissionais_id', table_name='categorizacoes_profissionais')
    op.drop_table('categorizacoes_profissionais')
