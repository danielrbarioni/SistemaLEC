from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from pydantic import BaseModel

from ..controllers import solicitacao_controller
from ..dependencies import get_solicitacao_provider, get_paciente_provider
from ..providers.interfaces.solicitacao_provider_interface import SolicitacaoProviderInterface
from ..providers.interfaces.paciente_provider_interface import PacienteProviderInterface
from sqlalchemy.ext.asyncio import AsyncSession
from ..resources.database import get_app_db_session
from ..auth.auth import auth_handler

import os
STRATEGY = os.getenv("SOLICITACOES_PROVIDER_TYPE", "sqlite")
PACIENTE_STRATEGY = os.getenv("PACIENTE_PROVIDER_TYPE", "sqlite")

router = APIRouter(
    prefix="/api/solicitacoes",
    tags=["Solicitacoes"],
    dependencies=[Depends(auth_handler.decode_token)]
)

class SolicitacaoCreate(BaseModel):
    tipo: str
    especialidade: str = ""
    procedimento: str = ""
    codigo_paciente: str
    nome_paciente: str
    judicializado: str = "Não"
    swalis: str = ""
    swallis: str = ""
    medico_responsavel: str = ""
    detalhes: str
    tempo_standby: int = None
    perfil_executor: str = ""
    usuario: str = ""
    procedimento_anterior: str = ""
    origem_menu: str = "Solicitações LEC"
    categorizacao: str = ""
    lateralidade: str = "Indefinida"

class SolicitacaoUpdate(BaseModel):
    especialidade: str = ""
    procedimento: str = ""
    codigo_paciente: str = ""
    nome_paciente: str = ""
    judicializado: str = "Não"
    swalis: str = ""
    swallis: str = ""
    medico_responsavel: str = ""
    detalhes: str = ""
    tempo_standby: int = None
    perfil_executor: str = ""
    usuario: str = ""
    procedimento_anterior: str = ""
    origem_menu: str = "Solicitações LEC"
    categorizacao: str = ""
    lateralidade: str = "Indefinida"

class SolicitacaoStatusUpdate(BaseModel):
    status: str
    perfil_executor: str = ""
    usuario: str = ""
    justificativa: str = ""

class StatusLocalUpdate(BaseModel):
    status_local: str

@router.post("", response_model=dict)
async def criar_solicitacao(
    solic: SolicitacaoCreate,
    provider: SolicitacaoProviderInterface = Depends(get_solicitacao_provider(STRATEGY)),
    paciente_provider: PacienteProviderInterface = Depends(get_paciente_provider(PACIENTE_STRATEGY)),
    user_info: dict = Depends(auth_handler.decode_token)
):
    """Envia uma nova solicitação (Inserir, Editar, Excluir, Stand-by)."""
    from .perfil import get_current_user_role
    role = get_current_user_role(user_info)
    if role in ["NENHUM", "OBSERVADOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solicite criação de usuário e associação a um perfil, no menu Perfis"
        )

    data = solic.model_dump()
    data["evento_tipo"] = "SOLICITACAO"
    if not data.get("usuario") and user_info:
        data["usuario"] = user_info.get("username") or user_info.get("sub") or user_info.get("name", "")
    return await solicitacao_controller.criar_solicitacao(data, provider, paciente_provider)

@router.get("", response_model=List[dict])
async def listar_solicitacoes(
    provider: SolicitacaoProviderInterface = Depends(get_solicitacao_provider(STRATEGY)),
    db: AsyncSession = Depends(get_app_db_session)
):
    """Lista todas as solicitações, resolvendo logins Ebserh de médicos responsáveis para seus Nomes Completos."""
    solics = await solicitacao_controller.listar_solicitacoes(provider)
    
    # Mapeia usernames para nomes completos a partir do banco de dados local
    try:
        from sqlalchemy import select
        from ..models.user import User
        result = await db.execute(select(User))
        usuarios = result.scalars().all()
        user_map = {u.username.lower().strip(): u.nome.strip() for u in usuarios if u.username and u.nome}
        
        for s in solics:
            medico = s.get('medico_responsavel')
            if medico:
                medico_clean = str(medico).strip()
                medico_lower = medico_clean.lower()
                if medico_lower in user_map:
                    s['medico_responsavel'] = user_map[medico_lower].upper()
                elif medico_clean not in ['Não informado', '—', '']:
                    s['medico_responsavel'] = medico_clean.upper()
    except Exception as e:
        pass
        
    return solics

@router.get("/paciente/{codigo_paciente}", response_model=dict)
async def obter_solicitacao_por_paciente(
    codigo_paciente: str,
    provider: SolicitacaoProviderInterface = Depends(get_solicitacao_provider(STRATEGY))
):
    """Retorna a solicitação mais recente cadastrada para um paciente específico."""
    solicitacoes = await solicitacao_controller.listar_solicitacoes(provider)
    solics_paciente = [s for s in solicitacoes if str(s.get('codigo_paciente')) == str(codigo_paciente)]
    if not solics_paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Nenhuma solicitação encontrada para este prontuário no Sistema LEC."
        )
    return solics_paciente[-1]

@router.put("/{id_solicitacao}", response_model=dict)
async def editar_solicitacao(
    id_solicitacao: str,
    solic_update: SolicitacaoUpdate,
    provider: SolicitacaoProviderInterface = Depends(get_solicitacao_provider(STRATEGY)),
    paciente_provider: PacienteProviderInterface = Depends(get_paciente_provider(PACIENTE_STRATEGY)),
    user_info: dict = Depends(auth_handler.decode_token)
):
    """Edita os dados de uma solicitação pendente e registra o evento de alteração no histórico."""
    from .perfil import get_current_user_role
    role = get_current_user_role(user_info)
    if role in ["NENHUM", "OBSERVADOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solicite criação de usuário e associação a um perfil, no menu Perfis"
        )

    data = solic_update.model_dump()
    perfil_executor = solic_update.perfil_executor or user_info.get("currentProfile") or role
    usuario_executor = solic_update.usuario or user_info.get("username") or user_info.get("sub") or user_info.get("name", "")

    return await solicitacao_controller.editar_solicitacao(
        id_solicitacao=id_solicitacao,
        dados_atualizados=data,
        provider=provider,
        paciente_provider=paciente_provider,
        perfil_executor=perfil_executor,
        usuario_executor=usuario_executor
    )

@router.put("/{id_solicitacao}/status", response_model=dict)
async def atualizar_status_solicitacao(
    id_solicitacao: str,
    status_update: SolicitacaoStatusUpdate,
    provider: SolicitacaoProviderInterface = Depends(get_solicitacao_provider(STRATEGY)),
    user_info: dict = Depends(auth_handler.decode_token)
):
    """Atualiza o status de processamento da solicitação e grava uma linha de Resposta no histórico."""
    from .perfil import get_current_user_role
    role = get_current_user_role(user_info)
    if role in ["NENHUM", "OBSERVADOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solicite criação de usuário e associação a um perfil, no menu Perfis"
        )

    novo_st = (status_update.status or "").upper()
    if novo_st in ["APROVADO", "REJEITADO"] and role not in ["ADMIN", "GESTAO_LEC"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas os perfis GESTÃO LEC e ADMIN podem aprovar ou rejeitar solicitações."
        )

    usuario_executor = status_update.usuario
    if not usuario_executor and user_info:
        usuario_executor = user_info.get("username") or user_info.get("sub") or user_info.get("name", "")

    return await solicitacao_controller.atualizar_status_solicitacao(
        id_solicitacao=id_solicitacao,
        novo_status=status_update.status,
        perfil_executor=status_update.perfil_executor,
        usuario_executor=usuario_executor,
        justificativa=status_update.justificativa,
        provider=provider
    )

@router.post("/{id_solicitacao}/cancelar-standby", response_model=dict)
async def cancelar_standby_solicitacao(
    id_solicitacao: int,
    provider: SolicitacaoProviderInterface = Depends(get_solicitacao_provider(STRATEGY)),
    user_info: dict = Depends(auth_handler.decode_token)
):
    """Solicita o cancelamento de um Standby ativo de uma solicitação."""
    from .perfil import get_current_user_role
    role = get_current_user_role(user_info)
    if role in ["NENHUM", "OBSERVADOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solicite criação de usuário e associação a um perfil, no menu Perfis"
        )

    return await solicitacao_controller.cancelar_standby_solicitacao(id_solicitacao, provider)

# Rotas extras para status locais sob o prefixo /api/pacientes para conveniência
pacientes_status_router = APIRouter(
    prefix="/api/pacientes",
    tags=["Pacientes - Status Locais"],
    dependencies=[Depends(auth_handler.decode_token)]
)

@pacientes_status_router.post("/{codigo_paciente}/status-local", response_model=dict)
async def salvar_status_local(
    codigo_paciente: str,
    status_update: StatusLocalUpdate,
    provider: SolicitacaoProviderInterface = Depends(get_solicitacao_provider(STRATEGY)),
    user_info: dict = Depends(auth_handler.decode_token)
):
    """Atualiza o status local de acompanhamento do paciente no hospital."""
    from .perfil import get_current_user_role
    role = get_current_user_role(user_info)
    if role in ["NENHUM", "OBSERVADOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solicite criação de usuário e associação a um perfil, no menu Perfis"
        )
    return await solicitacao_controller.salvar_status_local_paciente(codigo_paciente, status_update.status_local, provider)

@pacientes_status_router.get("/status-locais", response_model=Dict[str, str])
async def obter_status_locais(
    provider: SolicitacaoProviderInterface = Depends(get_solicitacao_provider(STRATEGY))
):
    """Lista todos os status locais associados aos pacientes."""
    return await solicitacao_controller.obter_status_locais_pacientes(provider)
