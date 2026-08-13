from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Request, Form
from typing import List, Optional
from sqlalchemy import select

from ..controllers import paciente_controller
from ..dependencies import get_paciente_provider
from ..providers.interfaces.paciente_provider_interface import PacienteProviderInterface

from ..auth.auth import auth_handler
from ..resources.database import get_app_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from ..helpers.excel_import_helper import process_excel_pacientes_import
from ..models.profile import Profile
from .perfil import get_current_user_role

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

@router.post("/importar-excel")
@router.post("/importar-excel/")
async def importar_planilha_excel(
    request: Request,
    file: UploadFile = File(...),
    especialidade: Optional[str] = Form(None),
    app_db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    """
    Importa planilha Excel contendo filas de pacientes por especialidade.
    Restrito ao perfil Gestão LEC. Exige a seleção de uma especialidade cadastrada.
    """
    role = get_current_user_role(current_user)
    current_profile = current_user.get("currentProfile") or current_user.get("perfil_tipo") or role

    if role not in ["ADMIN", "GESTAO_LEC"] and current_profile not in ["Gestão LEC", "GESTAO_LEC", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para o perfil Gestão LEC."
        )

    if not especialidade or not especialidade.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selecione uma especialidade válida para realizar a importação. Caso a especialidade não exista, crie-a primeiro na tela de Perfis."
        )

    especialidade_limpa = especialidade.strip()

    # Verificar se a especialidade/perfil existe no banco
    stmt_prof = select(Profile).where(
        (Profile.especialidade == especialidade_limpa) | 
        (Profile.nome == especialidade_limpa) |
        (Profile.id == especialidade_limpa.upper().replace(" ", "_"))
    )
    res_prof = await app_db.execute(stmt_prof)
    perfil_obj = res_prof.scalars().first()

    if not perfil_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"O perfil para a especialidade '{especialidade_limpa}' não foi encontrado no sistema. Por favor, crie este perfil na tela de Perfis antes de importar a planilha."
        )

    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de arquivo inválido. Por favor, envie um arquivo Excel (.xlsx ou .xls)."
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo enviado está vazio."
        )

    aghu_db = None
    if hasattr(request.app.state, "aghu_db") and request.app.state.aghu_db:
        try:
            aghu_manager = request.app.state.aghu_db
            async for sess in aghu_manager.get_session():
                aghu_db = sess
                break
        except Exception as e:
            print(f"Não foi possível obter sessão do AGHU para importação: {e}")

    usuario_executor = current_user.get("nome") or current_user.get("username") or "sistema"

    resultado = await process_excel_pacientes_import(
        file_bytes=contents,
        app_db=app_db,
        aghu_db=aghu_db,
        usuario_executor=usuario_executor,
        especialidade_override=perfil_obj.especialidade or perfil_obj.nome
    )

    return resultado

@router.get("/{codigo}", response_model=dict)
async def obter_paciente(
    codigo: str,
    provider: PacienteProviderInterface = Depends(get_paciente_provider(STRATEGY))
):
    """Obtém um paciente pelo código a partir da fonte de dados configurada no roteador."""
    codigo_int = int(codigo) if codigo.isdigit() else codigo
    return await paciente_controller.obter_paciente_por_codigo(codigo_int, provider)

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

