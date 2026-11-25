from sqlalchemy import Column, String, Text
from ..resources.database import Base

class NavegacaoConfig(Base):
    __tablename__ = "navegacao_config"

    id = Column(String, primary_key=True, index=True)
    config_json = Column(Text, nullable=False)
    data_atualizacao = Column(String, nullable=True)
    usuario_atualizacao = Column(String, nullable=True)
