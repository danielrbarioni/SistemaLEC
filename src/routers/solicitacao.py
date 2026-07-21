from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from pydantic import BaseModel

from ..controllers import solicitacao_controller
from ..dependencies import get_solicitacao_provider
from ..providers.interfaces.solicitacao_provider_interface import SolicitacaoProviderInterface
from ..auth.auth import auth_handler

import os
STRATEGY = os.getenv("SOLICITACOES_PROVIDER_TYPE", "sqlite")

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
    origem_menu: str = "Sistema LEC"

class SolicitacaoStatusUpdate(BaseModel):
    status: str

class StatusLocalUpdate(BaseModel):
    status_local: str

@router.post("", response_model=dict)
async def criar_solicitacao(
    solic: SolicitacaoCreate,
    provider: SolicitacaoProviderInterface = Depends(get_solicitacao_provider(STRATEGY)),
    user_info: dict = Depends(auth_handler.decode_token)
):
    """Envia uma nova solicitação (Inserir, Editar, Excluir, Stand-by)."""
    data = solic.model_dump()
    if not data.get("usuario") and user_info:
        display_name = user_info.get("displayName")
        if isinstance(display_name, list) and len(display_name) > 0:
            display_name = display_name[0]
        data["usuario"] = display_name or user_info.get("name") or user_info.get("username") or user_info.get("sub", "")
    return await solicitacao_controller.criar_solicitacao(data, provider)

@router.get("", response_model=List[dict])
async def listar_solicitacoes(
    provider: SolicitacaoProviderInterface = Depends(get_solicitacao_provider(STRATEGY))
):
    """Lista todas as solicitações."""
    return await solicitacao_controller.listar_solicitacoes(provider)

@router.get("/paciente/{codigo_paciente}", response_model=dict)
async def obter_solicitacao_por_paciente(
    codigo_paciente: str,
    provider: SolicitacaoProviderInterface = Depends(get_solicitacao_provider(STRATEGY))
):
    """Retorna a solicitação mais recente cadastrada para um paciente específico."""
    solicitacoes = await solicitacao_controller.listar_solicitacoes(provider)
    # Filtra por codigo_paciente e ordena para pegar a mais recente
    solics_paciente = [s for s in solicitacoes if str(s.get('codigo_paciente')) == str(codigo_paciente)]
    if not solics_paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Nenhuma solicitação encontrada para este prontuário no Sistema LEC."
        )
    # Retorna a última cadastrada
    return solics_paciente[-1]

@router.put("/{id_solicitacao}/status", response_model=dict)
async def atualizar_status_solicitacao(
    id_solicitacao: str,
    status_update: SolicitacaoStatusUpdate,
    provider: SolicitacaoProviderInterface = Depends(get_solicitacao_provider(STRATEGY))
):
    """Atualiza o status de processamento da solicitação."""
    return await solicitacao_controller.atualizar_status_solicitacao(id_solicitacao, status_update.status, provider)

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
    provider: SolicitacaoProviderInterface = Depends(get_solicitacao_provider(STRATEGY))
):
    """Atualiza o status local de acompanhamento do paciente no hospital."""
    return await solicitacao_controller.salvar_status_local_paciente(codigo_paciente, status_update.status_local, provider)

@pacientes_status_router.get("/status-locais", response_model=Dict[str, str])
async def obter_status_locais(
    provider: SolicitacaoProviderInterface = Depends(get_solicitacao_provider(STRATEGY))
):
    """Lista todos os status locais associados aos pacientes."""
    return await solicitacao_controller.obter_status_locais_pacientes(provider)
