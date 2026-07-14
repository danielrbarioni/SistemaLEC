from sqlalchemy import Column, Integer, String
from ..resources.database import Base

class Paciente(Base):
    __tablename__ = "pacientes"

    codigo = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    dt_nascimento = Column(String, nullable=True)
    cpf = Column(String, nullable=True)
    sexo = Column(String, nullable=True)
    cor = Column(String, nullable=True)
    nome_mae = Column(String, nullable=True)
    nome_pai = Column(String, nullable=True)
    data_hora_inicio = Column(String, nullable=True)
    status_consulta = Column(String, nullable=True)
    especialidade = Column(String, nullable=True)
    procedimento = Column(String, nullable=True)
    ultima_consulta_epo = Column(String, nullable=True)
