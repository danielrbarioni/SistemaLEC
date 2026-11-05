from sqlalchemy import Column, String, Text
from ..resources.database import Base


class DiagnosticoLec(Base):
    __tablename__ = "diagnosticos_lec"

    id = Column(String, primary_key=True, index=True)
    data_criacao = Column(String, nullable=False, index=True)
    usuario = Column(String, nullable=False)
    arquivos_json = Column(Text, nullable=True)
    resumo_json = Column(Text, nullable=False)
    detalhes_json = Column(Text, nullable=False)

