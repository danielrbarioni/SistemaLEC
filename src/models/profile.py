from sqlalchemy import Column, String
from ..resources.database import Base

class Profile(Base):
    __tablename__ = "perfis"

    id = Column(String, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    tipo = Column(String, nullable=False) # 'ADMIN', 'GESTAO_LEC', 'ESPECIALIDADE'
    cor = Column(String, nullable=False) # 'cinza', 'azul', 'verde'
    especialidade = Column(String, nullable=True)
