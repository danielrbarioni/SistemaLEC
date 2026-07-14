import os
from typing import Callable
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .providers.interfaces.paciente_provider_interface import PacienteProviderInterface
from .providers.implementations.paciente_postgres_provider import PacientePostgresProvider
from .providers.implementations.paciente_sqlite_provider import PacienteSqliteProvider
from .providers.implementations.paciente_csv_provider import PacienteCsvProvider
from .providers.implementations.paciente_hybrid_provider import HybridPacienteProvider

from .providers.interfaces.solicitacao_provider_interface import SolicitacaoProviderInterface
from .providers.implementations.solicitacao_csv_provider import SolicitacaoCsvProvider
from .providers.implementations.solicitacao_sqlite_provider import SolicitacaoSqliteProvider

from .resources.database import get_aghu_db_session, get_app_db_session

# 1. Funções "getter" simples e independentes (privadas por convenção)
def _get_paciente_postgres_provider(
    postgres_session: AsyncSession = Depends(get_aghu_db_session),
    sqlite_session: AsyncSession = Depends(get_app_db_session)
) -> PacienteProviderInterface:
    return HybridPacienteProvider(postgres_session=postgres_session, sqlite_session=sqlite_session)

def _get_paciente_sqlite_provider(
    session: AsyncSession = Depends(get_app_db_session)
) -> PacienteProviderInterface:
    return PacienteSqliteProvider(session=session)

def _get_paciente_csv_provider() -> PacienteProviderInterface:
    csv_path = os.getenv("PACIENTE_CSV_PATH", "data/pacientes.csv")
    return PacienteCsvProvider(csv_path=csv_path)

def _get_solicitacao_csv_provider() -> SolicitacaoProviderInterface:
    solicitacoes_path = os.getenv("SOLICITACOES_CSV_PATH", "data/solicitacoes.csv")
    status_locais_path = os.getenv("STATUS_LOCAIS_CSV_PATH", "data/status_locais.csv")
    return SolicitacaoCsvProvider(solicitacoes_path=solicitacoes_path, status_locais_path=status_locais_path)

def _get_solicitacao_sqlite_provider(
    session: AsyncSession = Depends(get_app_db_session)
) -> SolicitacaoProviderInterface:
    return SolicitacaoSqliteProvider(session=session)

# 2. A FÁBRICA: A única função que o roteador vai conhecer.
def get_paciente_provider(strategy: str) -> Callable[..., PacienteProviderInterface]:
    """
    Esta é uma fábrica. Baseado na string 'strategy', ela não retorna o provedor,
    mas sim a FUNÇÃO DE DEPENDÊNCIA correta que o FastAPI deve usar.
    """
    if strategy.upper() == "POSTGRES":
        return _get_paciente_postgres_provider
    elif strategy.upper() == "SQLITE":
        return _get_paciente_sqlite_provider
    elif strategy.upper() == "CSV":
        return _get_paciente_csv_provider
    else:
        raise ValueError(f"Estratégia de provedor desconhecida: {strategy}")

def get_solicitacao_provider(strategy: str) -> Callable[..., SolicitacaoProviderInterface]:
    if strategy.upper() == "SQLITE":
        return _get_solicitacao_sqlite_provider
    elif strategy.upper() == "CSV":
        return _get_solicitacao_csv_provider
    else:
        raise ValueError(f"Estratégia de provedor desconhecida: {strategy}")

