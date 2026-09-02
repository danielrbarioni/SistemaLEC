import json
from sqlalchemy import Column, Integer, String, Text, UniqueConstraint
from ..resources.database import Base

class CategorizacaoProfissional(Base):
    __tablename__ = "categorizacoes_profissionais"
    __table_args__ = (
        UniqueConstraint('medico', 'especialidade', name='uq_categorizacao_medico_especialidade'),
    )

    id = Column(Integer, primary_key=True, index=True)
    medico = Column(String, index=True, nullable=False)
    especialidade = Column(String, index=True, nullable=False)
    categorias_json = Column(Text, nullable=False, default="[]")

    @property
    def categorias(self):
        try:
            return json.loads(self.categorias_json or "[]")
        except Exception:
            return []

    @categorias.setter
    def categorias(self, val):
        self.categorias_json = json.dumps(val or [])
