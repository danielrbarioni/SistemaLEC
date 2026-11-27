from sqlalchemy import Column, Integer, String, Text
from ..resources.database import Base


class NavegacaoConfig(Base):
    __tablename__ = "navegacao_config"

    id = Column(String, primary_key=True, index=True)
    config_json = Column(Text, nullable=False)
    data_atualizacao = Column(String, nullable=True)
    usuario_atualizacao = Column(String, nullable=True)


class NavegacaoClassificacao(Base):
    __tablename__ = "navegacao_classificacoes"

    id = Column(String, primary_key=True, index=True)  # f"{pac_codigo}:{tabela_origem}"
    pac_codigo = Column(Integer, nullable=False, index=True)
    prontuario = Column(String, nullable=False, index=True)
    tabela_origem = Column(String, nullable=False, index=True)  # T1_2, T2, T3_2, T4
    numero_consulta_ref = Column(Integer, nullable=True)
    data_consulta_ref = Column(String, nullable=True)
    grade_sigla_ref = Column(String, nullable=True)
    status_consulta_ref = Column(String, nullable=True)
    classificacao = Column(String, nullable=False)
    requer_acao = Column(Integer, nullable=False, default=0)
    acao_realizada = Column(Integer, nullable=False, default=0)
    usuario_classificacao = Column(String, nullable=True)
    data_classificacao = Column(String, nullable=True)
    usuario_acao = Column(String, nullable=True)
    data_acao = Column(String, nullable=True)
