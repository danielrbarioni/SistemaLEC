from abc import ABC, abstractmethod
from typing import List, Dict, Any

class SolicitacaoProviderInterface(ABC):
    """Interface (contrato) para provedores de dados de solicitações e status locais."""

    @abstractmethod
    async def criar_solicitacao(self, solicitacao: Dict[str, Any]) -> Dict[str, Any]:
        """Cria uma nova solicitação (Inserir, Editar, Excluir, Stand-by)."""
        pass

    @abstractmethod
    async def listar_solicitacoes(self) -> List[Dict[str, Any]]:
        """Lista todas as solicitações enviadas."""
        pass

    @abstractmethod
    async def atualizar_status_solicitacao(self, id_solicitacao: str, novo_status: str) -> Dict[str, Any]:
        """Atualiza o status de uma solicitação (Pendente, Aprovada, Rejeitada)."""
        pass

    @abstractmethod
    async def salvar_status_local_paciente(self, codigo_paciente: str, status_local: str) -> Dict[str, Any]:
        """Salva o status local (HC-UFPE) de um paciente (ex: 'Exames Prontos')."""
        pass

    @abstractmethod
    async def obter_status_locais_pacientes(self) -> Dict[str, str]:
        """Retorna um mapeamento de código do paciente para seu status local."""
        pass
