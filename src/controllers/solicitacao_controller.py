from typing import List, Dict, Any, Optional
from ..providers.interfaces.solicitacao_provider_interface import SolicitacaoProviderInterface
from ..providers.interfaces.paciente_provider_interface import PacienteProviderInterface

from fastapi import HTTPException, status

async def criar_solicitacao(
    solicitacao: Dict[str, Any],
    provider: SolicitacaoProviderInterface,
    paciente_provider: Optional[PacienteProviderInterface] = None
) -> Dict[str, Any]:
    tipo = solicitacao.get("tipo", "INSERIR")
    
    if tipo == "INSERIR":
        codigo = str(solicitacao.get("codigo_paciente", "")).strip()
        nome_paciente = str(solicitacao.get("nome_paciente", "")).strip()
        especialidade = solicitacao.get("especialidade", "")
        procedimento = solicitacao.get("procedimento", "")
        
        if not codigo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número de prontuário é obrigatório."
            )
            
        if not nome_paciente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome do paciente é obrigatório."
            )
            
        # Validação do prontuário no AGHU / base de pacientes
        if paciente_provider:
            try:
                codigo_int = int(codigo) if codigo.isdigit() else codigo
                pac_data = await paciente_provider.obter_paciente_por_codigo(codigo_int)
                if pac_data and pac_data.get("nome") and not str(pac_data.get("nome", "")).lower().startswith("paciente #"):
                    # Garante que o nome cadastrado no AGHU é o utilizado na solicitação
                    solicitacao["nome_paciente"] = pac_data["nome"]
                else:
                    if not (nome_paciente.lower().startswith("prontuário") or "não identificado no aghu" in nome_paciente.lower()):
                        solicitacao["nome_paciente"] = f"Prontuário {codigo} não identificado no AGHU"
            except HTTPException as e:
                if e.status_code == status.HTTP_404_NOT_FOUND:
                    # Se o paciente não existir no AGHU, permite inclusão com o nome padronizado
                    if not (nome_paciente.lower().startswith("prontuário") or "não identificado no aghu" in nome_paciente.lower()):
                        solicitacao["nome_paciente"] = f"Prontuário {codigo} não identificado no AGHU"
                else:
                    raise e
        
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
            [s for s in solics_paciente if s.get("status") == "APROVADO" and s.get("evento_tipo") != "RESPOSTA"],
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
    provider: SolicitacaoProviderInterface,
    perfil_executor: str = "",
    usuario_executor: str = "",
    justificativa: str = ""
) -> Dict[str, Any]:
    return await provider.atualizar_status_solicitacao(
        id_solicitacao=id_solicitacao,
        novo_status=novo_status,
        perfil_executor=perfil_executor,
        usuario_executor=usuario_executor,
        justificativa=justificativa
    )

async def editar_solicitacao(
    id_solicitacao: str,
    dados_atualizados: Dict[str, Any],
    provider: SolicitacaoProviderInterface,
    paciente_provider: Optional[PacienteProviderInterface] = None,
    perfil_executor: str = "",
    usuario_executor: str = ""
) -> Dict[str, Any]:
    # 1. Busca a solicitação para validar existência e status
    solics = await provider.listar_solicitacoes()
    solic_original = next((s for s in solics if s.get("id") == id_solicitacao), None)
    
    if not solic_original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada."
        )
        
    if solic_original.get("status") != "PENDENTE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas solicitações com status PENDENTE podem ser editadas."
        )
        
    if solic_original.get("tipo") == "EXCLUIR":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solicitações de exclusão não podem ser editadas, apenas canceladas."
        )
        
    # Se a solicitação for de INSERIR e estiver atualizando o prontuário/paciente
    if solic_original.get("tipo") == "INSERIR":
        codigo = str(dados_atualizados.get("codigo_paciente", solic_original.get("codigo_paciente", ""))).strip()
        nome_paciente = str(dados_atualizados.get("nome_paciente", solic_original.get("nome_paciente", ""))).strip()
        if paciente_provider and codigo:
            try:
                codigo_int = int(codigo) if codigo.isdigit() else codigo
                pac_data = await paciente_provider.obter_paciente_por_codigo(codigo_int)
                if pac_data and pac_data.get("nome") and not str(pac_data.get("nome", "")).lower().startswith("paciente #"):
                    dados_atualizados["nome_paciente"] = pac_data["nome"]
                else:
                    if not (nome_paciente.lower().startswith("prontuário") or "não identificado no aghu" in nome_paciente.lower()):
                        dados_atualizados["nome_paciente"] = f"Prontuário {codigo} não identificado no AGHU"
            except HTTPException as e:
                if e.status_code == status.HTTP_404_NOT_FOUND:
                    if not (nome_paciente.lower().startswith("prontuário") or "não identificado no aghu" in nome_paciente.lower()):
                        dados_atualizados["nome_paciente"] = f"Prontuário {codigo} não identificado no AGHU"
                else:
                    raise e

    return await provider.editar_solicitacao(
        id_solicitacao=id_solicitacao,
        dados_atualizados=dados_atualizados,
        perfil_executor=perfil_executor,
        usuario_executor=usuario_executor
    )

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
