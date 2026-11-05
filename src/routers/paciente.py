from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Request, Form
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import select

from ..controllers import paciente_controller
from ..dependencies import get_paciente_provider
from ..providers.interfaces.paciente_provider_interface import PacienteProviderInterface

from ..auth.auth import auth_handler
from ..resources.database import get_app_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from ..helpers.excel_import_helper import process_excel_pacientes_import
from ..helpers.lec_diagnostico_helper import (
    executar_e_salvar_diagnostico_lec,
    listar_diagnosticos_lec,
    obter_diagnostico_lec,
    sincronizar_itens_diagnostico_no_cc,
)
from ..helpers.string_helper import generate_profile_id, remove_accents
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
    canonical_id = generate_profile_id(especialidade_limpa)
    norm_esp = remove_accents(especialidade_limpa).upper()

    # Verificar se a especialidade/perfil existe no banco
    stmt_prof = select(Profile)
    res_prof = await app_db.execute(stmt_prof)
    all_profiles = res_prof.scalars().all()
    
    perfil_obj = None
    for p in all_profiles:
        if p.id == canonical_id or (p.especialidade and remove_accents(p.especialidade).upper() == norm_esp) or (p.nome and remove_accents(p.nome).upper() == norm_esp):
            perfil_obj = p
            break

    if not perfil_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"O perfil para a especialidade '{especialidade_limpa}' não foi encontrado no sistema. Por favor, crie este perfil na tela de Perfis antes de importar a planilha."
        )

    # Usa o nome canônico e padronizado da especialidade
    especialidade_canonica = (perfil_obj.especialidade or perfil_obj.nome or especialidade_limpa).upper()

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
        especialidade_override=especialidade_canonica
    )

    return resultado


def _ensure_admin_or_gestao_lec(current_user: dict) -> None:
    role = get_current_user_role(current_user)
    current_profile = current_user.get("currentProfile") or current_user.get("perfil_tipo") or role
    if role not in ["ADMIN", "GESTAO_LEC"] and current_profile not in [
        "Gestão LEC",
        "GESTAO_LEC",
        "ADMIN",
        "Administrador",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para os perfis Administrador e Gestão LEC.",
        )


class SincronizarDiagnosticoPayload(BaseModel):
    item_ids: List[str]
    acao: Optional[str] = None
    dados_edicao: Optional[dict] = None


@router.get("/diagnostico-lec")
@router.get("/diagnostico-lec/")
async def listar_historico_diagnosticos_lec(
    app_db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token),
):
    """Lista os diagnósticos de sincronia realizados (do mais recente para o mais antigo)."""
    _ensure_admin_or_gestao_lec(current_user)
    return await listar_diagnosticos_lec(app_db)


@router.get("/diagnostico-lec/{diagnostico_id}")
async def obter_detalhes_diagnostico_lec(
    diagnostico_id: str,
    app_db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token),
):
    """Retorna todas as informações e divergências de um diagnóstico realizado."""
    _ensure_admin_or_gestao_lec(current_user)
    diag = await obter_diagnostico_lec(diagnostico_id, app_db)
    if not diag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnóstico não encontrado.")
    return diag


@router.post("/diagnostico-lec")
@router.post("/diagnostico-lec/")
async def criar_novo_diagnostico_lec(
    request: Request,
    files: List[UploadFile] = File(...),
    app_db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token),
):
    """
    Processa uma ou mais planilhas (.xlsx/.xls) ou pacotes .zip exportados do Sistema LEC,
    executa o diagnóstico de sincronia contra o Comunicação Cirúrgica e salva no histórico.
    """
    _ensure_admin_or_gestao_lec(current_user)
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Envie pelo menos um arquivo (.xlsx, .xls ou .zip).",
        )

    uploaded_tuples = []
    for f in files:
        fname = f.filename or ""
        if not fname.lower().endswith((".xlsx", ".xls", ".zip")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato de arquivo inválido ('{fname}'). Envie apenas arquivos .xlsx, .xls ou .zip.",
            )
        fbytes = await f.read()
        if fbytes:
            uploaded_tuples.append((fname, fbytes))

    if not uploaded_tuples:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Os arquivos enviados estão vazios.",
        )

    usuario_executor = current_user.get("nome") or current_user.get("username") or "Gestão LEC"
    try:
        resultado = await executar_e_salvar_diagnostico_lec(
            uploaded_files=uploaded_tuples,
            app_db=app_db,
            usuario_executor=usuario_executor,
        )
        return resultado
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@router.post("/diagnostico-lec/{diagnostico_id}/sincronizar")
async def sincronizar_divergencias_diagnostico_lec(
    diagnostico_id: str,
    payload: SincronizarDiagnosticoPayload,
    request: Request,
    app_db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token),
):
    """
    Executa ações de sincronização exclusivamente no banco de dados do Comunicação Cirúrgica
    para os itens selecionados de um diagnóstico (novo ou anterior).
    """
    _ensure_admin_or_gestao_lec(current_user)
    if not payload.item_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selecione ao menos um item para sincronizar.",
        )

    aghu_db = None
    if hasattr(request.app.state, "aghu_db") and request.app.state.aghu_db:
        try:
            aghu_manager = request.app.state.aghu_db
            async for sess in aghu_manager.get_session():
                aghu_db = sess
                break
        except Exception as e:
            print(f"Aviso: não foi possível abrir sessão AGHU na sincronização: {e}")

    usuario_executor = (
        current_user.get("username")
        or current_user.get("sub")
        or current_user.get("nome")
        or current_user.get("name")
        or "Gestão LEC"
    )
    role = get_current_user_role(current_user)
    perfil_executor = "Administrador" if role == "ADMIN" else "Gestão LEC"
    try:
        return await sincronizar_itens_diagnostico_no_cc(
            diagnostico_id=diagnostico_id,
            item_ids=payload.item_ids,
            acao_override=payload.acao,
            dados_edicao=payload.dados_edicao,
            app_db=app_db,
            aghu_db=aghu_db,
            usuario_executor=usuario_executor,
            perfil_executor=perfil_executor,
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))


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

