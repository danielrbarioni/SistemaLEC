from fastapi import APIRouter, Depends
from typing import List

from ..controllers import paciente_controller
# Alteração: Importamos apenas a FÁBRICA
from ..dependencies import get_paciente_provider
from ..providers.interfaces.paciente_provider_interface import PacienteProviderInterface

from ..auth.auth import auth_handler

import os
# --- PONTO ÚNICO DE CONFIGURAÇÃO PARA ESTE ROTEADOR ---
STRATEGY = os.getenv("PACIENTE_PROVIDER_TYPE", "sqlite")
# ----------------------------------------------------

router = APIRouter(
    prefix="/api/pacientes",
    tags=["Pacientes"],
    dependencies=[Depends(auth_handler.decode_token)]
)

@router.get("", response_model=List[dict])
async def listar_pacientes(
    # A mágica acontece aqui:
    # 1. get_paciente_provider(STRATEGY) retorna a função _get_paciente_csv_provider
    # 2. FastAPI efetivamente executa Depends(_get_paciente_csv_provider)
    provider: PacienteProviderInterface = Depends(get_paciente_provider(STRATEGY))
):
    """Lista todos os pacientes da fonte de dados configurada no roteador."""
    return await paciente_controller.listar_pacientes(provider)

@router.get("/{codigo}", response_model=dict)
async def obter_paciente(
    codigo: int,
    provider: PacienteProviderInterface = Depends(get_paciente_provider(STRATEGY))
):
    """Obtém um paciente pelo código a partir da fonte de dados configurada no roteador."""
    return await paciente_controller.obter_paciente_por_codigo(codigo, provider)

especialidade_router = APIRouter(
    prefix="/api/especialidades",
    tags=["Especialidades"],
    dependencies=[Depends(auth_handler.decode_token)]
)

@especialidade_router.get("/{id_especialidade}/procedimentos", response_model=List[dict])
async def obter_procedimentos_especialidade(
    id_especialidade: int,
    provider: PacienteProviderInterface = Depends(get_paciente_provider(STRATEGY))
):
    """Retorna os procedimentos cirúrgicos ativos associados a uma especialidade do AGHU."""
    return await provider.obter_procedimentos_por_especialidade(id_especialidade)
