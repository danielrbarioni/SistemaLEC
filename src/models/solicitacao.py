from sqlalchemy import Column, Integer, String
from ..resources.database import Base

class Solicitacao(Base):
    __tablename__ = "solicitacoes"

    id = Column(String, primary_key=True, index=True)
    tipo = Column(String, nullable=False)
    especialidade = Column(String, nullable=False)
    procedimento = Column(String, nullable=False)
    codigo_paciente = Column(Integer, index=True, nullable=False)
    nome_paciente = Column(String, nullable=False)
    judicializado = Column(String, nullable=True)
    swallis = Column(String, nullable=True)
    medico_responsavel = Column(String, nullable=True)
    detalhes = Column(String, nullable=True)
    tempo_standby = Column(Integer, nullable=True)
    status = Column(String, nullable=False)
    data_criacao = Column(String, nullable=False)
    perfil_executor = Column(String, nullable=True)
    usuario = Column(String, nullable=True)
    procedimento_anterior = Column(String, nullable=True)
    origem_menu = Column(String, nullable=True)
