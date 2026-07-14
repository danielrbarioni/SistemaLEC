from typing import List, Dict, Any
from ..providers.interfaces.solicitacao_provider_interface import SolicitacaoProviderInterface

from fastapi import HTTPException, status

async def criar_solicitacao(
    solicitacao: Dict[str, Any],
    provider: SolicitacaoProviderInterface
) -> Dict[str, Any]:
    tipo = solicitacao.get("tipo", "INSERIR")
    
    if tipo == "INSERIR":
        codigo = str(solicitacao.get("codigo_paciente", ""))
        especialidade = solicitacao.get("especialidade", "")
        procedimento = solicitacao.get("procedimento", "")
        
        # Obter todas as solicitações para verificar se já existe na fila
        solics = await provider.listar_solicitacoes()
        solics_paciente = [s for s in solics if str(s.get("codigo_paciente")) == codigo]
        
        # 1. Verifica se já existe uma solicitação de inclusão PENDENTE idêntica
        pendente = any(
            s.get("tipo") == "INSERIR" and 
            s.get("especialidade") == especialidade and 
            s.get("procedimento") == procedimento and 
            s.get("status") == "PENDENTE"
            for s in solics_paciente
        )
        if pendente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe uma solicitação de inclusão PENDENTE para o procedimento '{procedimento}' na especialidade '{especialidade}'. Aguarde a análise da Gestão LEC."
            )
            
        # 2. Reconstrói os procedimentos ATIVOS (aprovados) para ver se já está inserido
        proc_map = {}
        # Ordena por data_criacao para simular a ordem correta dos acontecimentos
        approved_solics = sorted(
            [s for s in solics_paciente if s.get("status") == "APROVADO"],
            key=lambda x: x.get("data_criacao", "")
        )
        
        for s in approved_solics:
            s_tipo = s.get("tipo")
            s_esp = s.get("especialidade")
            s_proc = s.get("procedimento")
            key = f"{s_esp}||{s_proc}"
            
            if s_tipo == "INSERIR":
                proc_map[key] = True
            elif s_tipo == "EDITAR":
                old_key = f"{s_esp}||{s.get('procedimento_anterior') or s_proc}"
                if old_key in proc_map:
                    del proc_map[old_key]
                proc_map[key] = True
            elif s_tipo == "EXCLUIR":
                if key in proc_map:
                    del proc_map[key]
                    
        target_key = f"{especialidade}||{procedimento}"
        if target_key in proc_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Este paciente já está cadastrado ativamente no procedimento '{procedimento}' na especialidade '{especialidade}'. Caso queira alterar dados, solicite a edição deste procedimento na aba correspondente."
            )

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
