from typing import List, Dict, Any
from ..providers.interfaces.solicitacao_provider_interface import SolicitacaoProviderInterface

async def criar_solicitacao(
    solicitacao: Dict[str, Any],
    provider: SolicitacaoProviderInterface
) -> Dict[str, Any]:
    return await provider.criar_solicitacao(solicitacao)

async def listar_solicitacoes(
    provider: SolicitacaoProviderInterface
) -> List[Dict[str, Any]]:
    return await provider.listar_solicitacoes()

async def atualizar_status_solicitacao(
    id_solicitacao: str,
    novo_status: str,
    provider: SolicitacaoProviderInterface
) -> Dict[str, Any]:
    return await provider.atualizar_status_solicitacao(id_solicitacao, novo_status)

async def salvar_status_local_paciente(
    codigo_paciente: str,
    status_local: str,
    provider: SolicitacaoProviderInterface
) -> Dict[str, Any]:
    return await provider.salvar_status_local_paciente(codigo_paciente, status_local)

async def obter_status_locais_pacientes(
    provider: SolicitacaoProviderInterface
) -> Dict[str, str]:
    return await provider.obter_status_locais_pacientes()
