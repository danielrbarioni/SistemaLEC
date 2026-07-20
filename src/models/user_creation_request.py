from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from ..resources.database import Base

class UserCreationRequest(Base):
    __tablename__ = "solicitacoes_criacao_usuario"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False)
    nome = Column(String, nullable=False)
    perfil_id = Column(String, nullable=False)
    especialidade = Column(String, nullable=True)
    funcao = Column(String, nullable=True) # "Médico", "Residente", "Enfermeiro"
    status = Column(String, default="PENDENTE", nullable=False) # "PENDENTE", "APROVADO", "REJEITADO"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    tipo = Column(String, default="CRIACAO", nullable=False) # "CRIACAO" or "EDICAO"
    user_id = Column(Integer, nullable=True)
    campos_modificados = Column(String, nullable=True) # JSON/text storing what changed
