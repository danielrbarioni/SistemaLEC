from sqlalchemy import Column, Integer, String
from ..resources.database import Base

class StatusLocal(Base):
    __tablename__ = "status_locais"

    codigo_paciente = Column(Integer, primary_key=True, index=True)
    status_local = Column(String, nullable=False)
    data_atualizacao = Column(String, nullable=False)
