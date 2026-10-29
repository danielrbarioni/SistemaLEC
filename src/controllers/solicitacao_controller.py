from typing import List, Dict, Any, Optional, Set
from ..providers.interfaces.solicitacao_provider_interface import SolicitacaoProviderInterface
from ..providers.interfaces.paciente_provider_interface import PacienteProviderInterface
from ..helpers.string_helper import normalizar_nome_base_procedimento, normalize_specialty_name

from fastapi import HTTPException, status


def _is_evento_log(s: Dict[str, Any]) -> bool:
    evento = str(s.get("evento_tipo") or "SOLICITACAO").strip().upper()
    return evento in ("RESPOSTA", "ALTERACAO", "EDICAO", "CANCELAMENTO") or bool(s.get("is_resposta"))


def _obter_procedimentos_ativos_normalizados(
    solics_paciente: List[Dict[str, Any]],
    pac_data: Optional[Dict[str, Any]] = None
) -> Set[str]:
    """
    Reconstrói o conjunto de nomes base normalizados dos procedimentos ativos
    de um paciente em Pacientes (considerando o cadastro base e o histórico de
    solicitações aprovadas de inclusão, edição e exclusão).
    """
    ativos: List[Dict[str, str]] = []

    if pac_data and pac_data.get("procedimento"):
        p_norm = normalizar_nome_base_procedimento(pac_data.get("procedimento"))
        e_norm = normalize_specialty_name(str(pac_data.get("especialidade") or ""))
        if p_norm:
            ativos.append({"esp": e_norm, "proc": p_norm})

    approved_solics = sorted(
        [
            s for s in solics_paciente
            if s.get("status") == "APROVADO" and not _is_evento_log(s)
        ],
        key=lambda x: str(x.get("data_criacao") or "")
    )

    for s in approved_solics:
        s_tipo = str(s.get("tipo") or "").upper()
        s_esp = normalize_specialty_name(str(s.get("especialidade") or ""))
        s_proc = normalizar_nome_base_procedimento(s.get("procedimento"))
        s_proc_ant = normalizar_nome_base_procedimento(s.get("procedimento_anterior") or s.get("procedimento"))

        if not s_proc:
            continue

        if s_tipo == "INSERIR":
            if not any(item["proc"] == s_proc and item["esp"] == s_esp for item in ativos):
                ativos.append({"esp": s_esp, "proc": s_proc})
        elif s_tipo in ("EDITAR", "EDICAO"):
            replaced = False
            for item in ativos:
                if item["proc"] == s_proc_ant and (not s_esp or not item["esp"] or item["esp"] == s_esp):
                    item["proc"] = s_proc
                    if s_esp:
                        item["esp"] = s_esp
                    replaced = True
                    break
            if not replaced:
                ativos.append({"esp": s_esp, "proc": s_proc})
        elif s_tipo == "EXCLUIR":
            for idx, item in enumerate(ativos):
                if item["proc"] == s_proc and (not s_esp or not item["esp"] or item["esp"] == s_esp):
                    ativos.pop(idx)
                    break

    return {item["proc"] for item in ativos if item.get("proc")}


def _validar_duplicidade_paciente_procedimento(
    tipo: str,
    codigo: str,
    procedimento: str,
    procedimento_anterior: str,
    solics: List[Dict[str, Any]],
    pac_data: Optional[Dict[str, Any]] = None,
    ignore_solic_id: Optional[str] = None
) -> None:
    """
    Valida e bloqueia (com HTTPException 400) solicitações duplicadas para a mesma dupla
    paciente + procedimento:
    - INSERIR: quando paciente + procedimento já existir em Pacientes ou já tiver INSERIR pendente
    - EDITAR: quando paciente + procedimento já tiver EDITAR pendente (ou novo procedimento já existir)
    - STANDBY / CANCELAR_STANDBY: quando paciente + procedimento já tiver STANDBY pendente
    - EXCLUIR: quando paciente + procedimento já tiver EXCLUIR pendente
    """
    tipo_upper = (tipo or "INSERIR").strip().upper()
    proc_norm = normalizar_nome_base_procedimento(procedimento)
    proc_ant_norm = normalizar_nome_base_procedimento(procedimento_anterior or procedimento)

    solics_paciente = [
        s for s in solics
        if str(s.get("codigo_paciente", "")).strip() == codigo
        and (not ignore_solic_id or str(s.get("id", "")) != str(ignore_solic_id))
    ]

    pendentes_reais = [
        s for s in solics_paciente
        if s.get("status") == "PENDENTE" and not _is_evento_log(s)
    ]

    ativos_norm = _obter_procedimentos_ativos_normalizados(solics_paciente, pac_data)

    if tipo_upper == "INSERIR":
        pendente_inserir = any(
            str(s.get("tipo") or "").upper() == "INSERIR"
            and normalizar_nome_base_procedimento(s.get("procedimento")) == proc_norm
            for s in pendentes_reais
        )
        if pendente_inserir:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é permitido solicitar inclusão: já existe uma solicitação de inclusão PENDENTE para o paciente (#{codigo}) e o procedimento '{procedimento}'. Aguarde a análise da Gestão LEC."
            )

        if proc_norm and proc_norm in ativos_norm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é permitido solicitar inclusão: o paciente (#{codigo}) já possui o procedimento '{procedimento}' cadastrado no banco de dados (Pacientes). Caso queira alterar dados, solicite a edição na aba correspondente."
            )

    elif tipo_upper in ("EDITAR", "EDICAO"):
        proc_exibicao = procedimento_anterior or procedimento
        pendente_editar = any(
            str(s.get("tipo") or "").upper() in ("EDITAR", "EDICAO")
            and (
                normalizar_nome_base_procedimento(s.get("procedimento_anterior") or s.get("procedimento")) in (proc_ant_norm, proc_norm)
                or normalizar_nome_base_procedimento(s.get("procedimento")) in (proc_ant_norm, proc_norm)
            )
            for s in pendentes_reais
        )
        if pendente_editar:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é permitido solicitar edição: já existe uma solicitação de edição PENDENTE para o paciente (#{codigo}) e o procedimento '{proc_exibicao}'. Aguarde a análise da Gestão LEC."
            )

        # Se a edição estiver alterando o procedimento para outro, garante que o novo procedimento não gere duplicidade no paciente
        if proc_norm and proc_ant_norm and proc_norm != proc_ant_norm:
            if proc_norm in ativos_norm:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Não é permitido alterar para o procedimento '{procedimento}': o paciente (#{codigo}) já possui este procedimento cadastrado no banco de dados (Pacientes)."
                )
            pendente_inserir_novo = any(
                str(s.get("tipo") or "").upper() == "INSERIR"
                and normalizar_nome_base_procedimento(s.get("procedimento")) == proc_norm
                for s in pendentes_reais
            )
            if pendente_inserir_novo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Não é permitido alterar para o procedimento '{procedimento}': já existe uma solicitação de inclusão PENDENTE para este paciente e procedimento."
                )

    elif tipo_upper in ("STANDBY", "CANCELAR_STANDBY"):
        pendente_standby = any(
            str(s.get("tipo") or "").upper() in ("STANDBY", "CANCELAR_STANDBY")
            and normalizar_nome_base_procedimento(s.get("procedimento")) == proc_norm
            for s in pendentes_reais
        )
        if pendente_standby:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é permitido solicitar standby: já existe uma solicitação de standby PENDENTE para o paciente (#{codigo}) e o procedimento '{procedimento}'. Aguarde a análise da Gestão LEC."
            )

    elif tipo_upper == "EXCLUIR":
        pendente_excluir = any(
            str(s.get("tipo") or "").upper() == "EXCLUIR"
            and normalizar_nome_base_procedimento(s.get("procedimento")) == proc_norm
            for s in pendentes_reais
        )
        if pendente_excluir:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é permitido solicitar exclusão: já existe uma solicitação de exclusão PENDENTE para o paciente (#{codigo}) e o procedimento '{procedimento}'. Aguarde a análise da Gestão LEC."
            )


async def criar_solicitacao(
    solicitacao: Dict[str, Any],
    provider: SolicitacaoProviderInterface,
    paciente_provider: Optional[PacienteProviderInterface] = None
) -> Dict[str, Any]:
    tipo = solicitacao.get("tipo", "INSERIR")
    
    # Tratamento de Lateralidade
    if "lateralidade" in solicitacao and solicitacao["lateralidade"]:
        lat_clean = str(solicitacao["lateralidade"]).strip()
        solicitacao["lateralidade"] = lat_clean
    else:
        solicitacao["lateralidade"] = "Indefinida"

    codigo = str(solicitacao.get("codigo_paciente", "")).strip()
    pac_data: Optional[Dict[str, Any]] = None

    if tipo == "INSERIR":
        nome_paciente = str(solicitacao.get("nome_paciente", "")).strip()
        especialidade = str(solicitacao.get("especialidade", "")).strip()
        procedimento = str(solicitacao.get("procedimento", "")).strip()
        medico_responsavel = str(solicitacao.get("medico_responsavel", "")).strip()
        
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

        if not especialidade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Especialidade é obrigatória."
            )

        if not procedimento:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Procedimento (Fila de Espera) é obrigatório."
            )

        if not medico_responsavel or medico_responsavel in ["—", "Não informado"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Médico Responsável é obrigatório."
            )
            
        # Validação do prontuário no AGHU / base de pacientes
        if paciente_provider:
            try:
                codigo_int = int(codigo) if codigo.isdigit() else codigo
                pac_data = await paciente_provider.obter_paciente_por_codigo(codigo_int)
                if pac_data and pac_data.get("nome") and not str(pac_data.get("nome", "")).lower().startswith("paciente #"):
                    # Garante que o nome cadastrado no AGHU (priorizando Nome Social) é o utilizado na solicitação
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
    else:
        if paciente_provider and codigo and codigo != "0":
            try:
                codigo_int = int(codigo) if codigo.isdigit() else codigo
                pac_data = await paciente_provider.obter_paciente_por_codigo(codigo_int)
                if pac_data and pac_data.get("nome") and not str(pac_data.get("nome", "")).lower().startswith("paciente #"):
                    solicitacao["nome_paciente"] = pac_data["nome"]
            except Exception:
                pass

    solics = await provider.listar_solicitacoes()
    _validar_duplicidade_paciente_procedimento(
        tipo=tipo,
        codigo=codigo,
        procedimento=str(solicitacao.get("procedimento", "")).strip(),
        procedimento_anterior=str(solicitacao.get("procedimento_anterior", "")).strip(),
        solics=solics,
        pac_data=pac_data
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
        
    if "procedimento" in dados_atualizados and not str(dados_atualizados.get("procedimento", "")).strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Procedimento (Fila de Espera) não pode ser vazio."
        )

    codigo = str(dados_atualizados.get("codigo_paciente", solic_original.get("codigo_paciente", ""))).strip()
    nome_paciente = str(dados_atualizados.get("nome_paciente", solic_original.get("nome_paciente", ""))).strip()
    pac_data: Optional[Dict[str, Any]] = None
    if paciente_provider and codigo and codigo != "0":
        try:
            codigo_int = int(codigo) if codigo.isdigit() else codigo
            pac_data = await paciente_provider.obter_paciente_por_codigo(codigo_int)
            if pac_data and pac_data.get("nome") and not str(pac_data.get("nome", "")).lower().startswith("paciente #"):
                dados_atualizados["nome_paciente"] = pac_data["nome"]
            elif solic_original.get("tipo") == "INSERIR":
                if not (nome_paciente.lower().startswith("prontuário") or "não identificado no aghu" in nome_paciente.lower()):
                    dados_atualizados["nome_paciente"] = f"Prontuário {codigo} não identificado no AGHU"
        except HTTPException as e:
            if e.status_code == status.HTTP_404_NOT_FOUND:
                if solic_original.get("tipo") == "INSERIR" and not (nome_paciente.lower().startswith("prontuário") or "não identificado no aghu" in nome_paciente.lower()):
                    dados_atualizados["nome_paciente"] = f"Prontuário {codigo} não identificado no AGHU"
            elif solic_original.get("tipo") == "INSERIR":
                raise e
        except Exception:
            pass

    tipo_solic = str(solic_original.get("tipo") or "INSERIR")
    procedimento_final = str(dados_atualizados.get("procedimento", solic_original.get("procedimento", ""))).strip()
    procedimento_ant_final = str(dados_atualizados.get("procedimento_anterior", solic_original.get("procedimento_anterior", ""))).strip()

    _validar_duplicidade_paciente_procedimento(
        tipo=tipo_solic,
        codigo=codigo,
        procedimento=procedimento_final,
        procedimento_anterior=procedimento_ant_final,
        solics=solics,
        pac_data=pac_data,
        ignore_solic_id=id_solicitacao
    )

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
