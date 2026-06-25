from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from pydantic import BaseModel

from ..controllers import solicitacao_controller
from ..dependencies import get_solicitacao_provider
from ..providers.interfaces.solicitacao_provider_interface import SolicitacaoProviderInterface
from ..auth.auth import auth_handler

STRATEGY = "csv"

router = APIRouter(
    prefix="/api/solicitacoes",
    tags=["Solicitacoes"],
    dependencies=[Depends(auth_handler.decode_token)]
)

class SolicitacaoCreate(BaseModel):
    tipo: str
    codigo_paciente: str
    nome_paciente: str
    detalhes: str

class SolicitacaoStatusUpdate(BaseModel):
    status: str

class StatusLocalUpdate(BaseModel):
    status_local: str

@router.post("", response_model=dict)
async def criar_solicitacao(
    solic: SolicitacaoCreate,
    provider: SolicitacaoProviderInterface = Depends(get_solicitacao_provider(STRATEGY))
):
    """Envia uma nova solicitação (Inserir, Editar, Excluir, Stand-by)."""
    return await solicitacao_controller.criar_solicitacao(solic.model_dump(), provider)

@router.get("", response_model=List[dict])
async def listar_solicitacoes(
    provider: SolicitacaoProviderInterface = Depends(get_solicitacao_provider(STRATEGY))
):
    """Lista todas as solicitações."""
    return await solicitacao_controller.listar_solicitacoes(provider)

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
