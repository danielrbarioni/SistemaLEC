from sqlalchemy import Column, Integer, String
from ..resources.database import Base

class User(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    nome = Column(String, nullable=False)
    perfil_id = Column(String, nullable=False) # Armazena o ID ou nome do perfil do usuário
    especialidade = Column(String, nullable=True) # Se for perfil Especialidade
