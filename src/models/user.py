from sqlalchemy import Column, Integer, String, UniqueConstraint
from ..resources.database import Base

class User(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        UniqueConstraint('username', 'perfil_id', name='uq_usuarios_username_perfil'),
    )

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False)
    nome = Column(String, nullable=True)
    perfil_id = Column(String, nullable=False) # Armazena o ID ou nome do perfil do usuário
    especialidade = Column(String, nullable=True) # Se for perfil Especialidade
    funcao = Column(String, nullable=True) # "Médico", "Residente", "Administrativo", "Enfermeiro" (para especialidades)

