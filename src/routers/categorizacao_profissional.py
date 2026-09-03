import json
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from ..auth.auth import auth_handler
from ..resources.database import get_app_db_session
from ..models.categorizacao_profissional import CategorizacaoProfissional
from ..models.solicitacao import Solicitacao
from ..models.paciente import Paciente
from ..helpers.historico_helper import registrar_evento_historico
from .perfil import get_current_user_role

router = APIRouter(
    prefix="/api/categorizacoes-profissionais",
    tags=["Categorização Profissional"],
    dependencies=[Depends(auth_handler.decode_token)]
)

class CategorizacaoCreate(BaseModel):
    medico: str
    especialidade: str
    categorias: List[str]

class CategorizacaoUpdate(BaseModel):
    categorias: List[str]
    renomeacoes: Optional[Dict[str, str]] = None  # Ex: {"Cat Antiga": "Cat Nova"}

class CategorizacaoResponse(BaseModel):
    id: int
    medico: str
    especialidade: str
    categorias: List[str]

    class Config:
        from_attributes = True

def check_admin_or_gestao(current_user: dict):
    role = get_current_user_role(current_user)
    current_profile = current_user.get("currentProfile") or current_user.get("perfil_tipo") or role
    
    allowed = ["ADMIN", "GESTAO_LEC"]
    allowed_names = ["Gestão LEC", "GESTAO_LEC", "ADMIN"]
    
    if role not in allowed and current_profile not in allowed_names:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ação permitida apenas para perfis ADMIN ou GESTÃO LEC."
        )

@router.get("", response_model=List[CategorizacaoResponse])
async def listar_categorizacoes(
    medico: Optional[str] = Query(None),
    especialidade: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_app_db_session)
):
    stmt = select(CategorizacaoProfissional)
    if medico:
        stmt = stmt.where(CategorizacaoProfissional.medico == medico.strip().upper())
    if especialidade:
        stmt = stmt.where(CategorizacaoProfissional.especialidade == especialidade.strip().upper())

    result = await db.execute(stmt)
    records = result.scalars().all()

    response = []
    for r in records:
        try:
            cats = json.loads(r.categorias_json or "[]")
        except Exception:
            cats = []
        response.append(
            CategorizacaoResponse(
                id=r.id,
                medico=r.medico,
                especialidade=r.especialidade,
                categorias=cats
            )
        )
    return response

@router.post("", response_model=CategorizacaoResponse, status_code=status.HTTP_201_CREATED)
async def criar_categorizacao(
    data: CategorizacaoCreate,
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    check_admin_or_gestao(current_user)

    medico_norm = data.medico.strip().upper()
    esp_norm = data.especialidade.strip().upper()
    
    # Filtra e limpa lista de categorias (sem vazios ou duplicatas preservando ordem)
    clean_cats = []
    for c in data.categorias:
        c_strip = c.strip()
        if c_strip and c_strip not in clean_cats:
            clean_cats.append(c_strip)

    if not clean_cats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="É necessário informar ao menos uma categoria válida."
        )

    # Verifica se já existe categorização para este médico nesta especialidade
    stmt_check = select(CategorizacaoProfissional).where(
        CategorizacaoProfissional.medico == medico_norm,
        CategorizacaoProfissional.especialidade == esp_norm
    )
    res_check = await db.execute(stmt_check)
    existing = res_check.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe uma categorização cadastrada para o médico '{medico_norm}' na especialidade '{esp_norm}'. Utilize a opção de edição."
        )

    novo = CategorizacaoProfissional(
        medico=medico_norm,
        especialidade=esp_norm,
        categorias_json=json.dumps(clean_cats, ensure_ascii=False)
    )
    db.add(novo)

    # Registra evento no Histórico
    role = get_current_user_role(current_user)
    perfil_exec = current_user.get("perfil_tipo") or current_user.get("currentProfile") or role
    await registrar_evento_historico(
        db=db,
        tipo="CRIAR_CATEGORIZACAO",
        origem_menu="Usuários",
        evento_tipo="EXECUCAO",
        detalhes=f'Categorização criada para o profissional {medico_norm} na especialidade {esp_norm}: {", ".join(clean_cats)}',
        status="CONCLUIDO",
        especialidade=esp_norm,
        procedimento="—",
        perfil_executor=perfil_exec,
        usuario=current_user.get("username", "")
    )

    await db.commit()
    await db.refresh(novo)

    return CategorizacaoResponse(
        id=novo.id,
        medico=novo.medico,
        especialidade=novo.especialidade,
        categorias=clean_cats
    )

@router.put("/{cat_id}", response_model=CategorizacaoResponse)
async def atualizar_categorizacao(
    cat_id: int,
    data: CategorizacaoUpdate,
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    check_admin_or_gestao(current_user)

    stmt = select(CategorizacaoProfissional).where(CategorizacaoProfissional.id == cat_id)
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categorização não encontrada."
        )

    try:
        old_cats = json.loads(record.categorias_json or "[]")
    except Exception:
        old_cats = []

    clean_new_cats = []
    for c in data.categorias:
        c_strip = c.strip()
        if c_strip and c_strip not in clean_new_cats:
            clean_new_cats.append(c_strip)

    if not clean_new_cats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A lista de categorias não pode ficar vazia. Para excluir todas, use a exclusão da categorização."
        )

    renomeacoes = data.renomeacoes or {}

    # 1. Trata renomeações de categorias nas solicitações e pacientes
    for de, para in renomeacoes.items():
        if de and para and de != para:
            # Atualiza solicitações onde medico e especialidade batem
            await db.execute(
                update(Solicitacao)
                .where(
                    Solicitacao.especialidade == record.especialidade,
                    Solicitacao.categorizacao == de
                )
                .values(categorizacao=para)
            )
            # Atualiza pacientes
            await db.execute(
                update(Paciente)
                .where(
                    Paciente.especialidade == record.especialidade,
                    Paciente.categorizacao == de
                )
                .values(categorizacao=para)
            )

    # 2. Trata categorias que foram excluídas da lista (que não foram renomeadas)
    for old_c in old_cats:
        if old_c not in clean_new_cats and old_c not in renomeacoes:
            await db.execute(
                update(Solicitacao)
                .where(
                    Solicitacao.especialidade == record.especialidade,
                    Solicitacao.categorizacao == old_c
                )
                .values(categorizacao=None)
            )
            await db.execute(
                update(Paciente)
                .where(
                    Paciente.especialidade == record.especialidade,
                    Paciente.categorizacao == old_c
                )
                .values(categorizacao=None)
            )

    record.categorias_json = json.dumps(clean_new_cats, ensure_ascii=False)

    # Registra evento no Histórico
    role = get_current_user_role(current_user)
    perfil_exec = current_user.get("perfil_tipo") or current_user.get("currentProfile") or role
    await registrar_evento_historico(
        db=db,
        tipo="EDITAR_CATEGORIZACAO",
        origem_menu="Usuários",
        evento_tipo="EXECUCAO",
        detalhes=f'Categorização do profissional {record.medico} na especialidade {record.especialidade} editada: {", ".join(clean_new_cats)}',
        status="CONCLUIDO",
        especialidade=record.especialidade,
        procedimento="—",
        perfil_executor=perfil_exec,
        usuario=current_user.get("username", "")
    )

    await db.commit()
    await db.refresh(record)

    return CategorizacaoResponse(
        id=record.id,
        medico=record.medico,
        especialidade=record.especialidade,
        categorias=clean_new_cats
    )

@router.delete("/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_categorizacao(
    cat_id: int,
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    check_admin_or_gestao(current_user)

    stmt = select(CategorizacaoProfissional).where(CategorizacaoProfissional.id == cat_id)
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categorização não encontrada."
        )

    # Desvincula todas as solicitações e pacientes do médico/especialidade que tinham categorização
    await db.execute(
        update(Solicitacao)
        .where(
            Solicitacao.especialidade == record.especialidade,
            Solicitacao.medico_responsavel == record.medico
        )
        .values(categorizacao=None)
    )
    await db.execute(
        update(Paciente)
        .where(
            Paciente.especialidade == record.especialidade
        )
        .values(categorizacao=None)
    )

    # Registra evento no Histórico
    role = get_current_user_role(current_user)
    perfil_exec = current_user.get("perfil_tipo") or current_user.get("currentProfile") or role
    await registrar_evento_historico(
        db=db,
        tipo="EXCLUIR_CATEGORIZACAO",
        origem_menu="Usuários",
        evento_tipo="EXECUCAO",
        detalhes=f'Categorização excluída do profissional {record.medico} na especialidade {record.especialidade}',
        status="CONCLUIDO",
        especialidade=record.especialidade,
        procedimento="—",
        perfil_executor=perfil_exec,
        usuario=current_user.get("username", "")
    )

    await db.delete(record)
    await db.commit()
    return None
