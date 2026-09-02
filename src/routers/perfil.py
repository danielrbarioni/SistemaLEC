# src/routers/perfil.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..helpers.string_helper import generate_profile_id, remove_accents

from ..auth.auth import auth_handler
from ..resources.database import get_app_db_session
from ..models.profile import Profile
from ..models.user import User
from ..helpers.historico_helper import registrar_evento_historico

router = APIRouter(prefix="/api/perfis", tags=["Perfis"])

class PerfilCreate(BaseModel):
    nome: str
    especialidade: Optional[str] = None

class PerfilAtivarRequest(BaseModel):
    perfil_id: str

class PerfilResponse(BaseModel):
    id: str
    nome: str
    tipo: str
    cor: str
    especialidade: Optional[str] = None

    class Config:
        from_attributes = True

def get_current_user_role(current_user: dict) -> str:
    """
    Retorna o tipo de perfil do usuário atual com base no token JWT.
    """
    # Se perfil_tipo foi injetado diretamente no JWT
    if "perfil_tipo" in current_user:
        return current_user["perfil_tipo"]
    
    # Fallback para AD/Mock usando grupos
    groups = current_user.get("groups", [])
    if "GLO-SEC-HCPE-SETISD" in groups:
        return "ADMIN"
    elif "GESTAO_LEC" in groups:
        return "GESTAO_LEC"
    elif "NENHUM" in groups or "OBSERVADOR" in groups:
        return "NENHUM"
    elif "ESPECIALIDADE" in groups:
        return "ESPECIALIDADE"
    
    # Se o username for admin, assume ADMIN
    if current_user.get("username") == "admin":
        return "ADMIN"
        
    return "NENHUM"  # Default fallback seguro para usuários sem perfil cadastrado

@router.get("", response_model=List[PerfilResponse])
async def get_perfis(
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    """
    Retorna a lista de todos os perfis cadastrados no banco local, incluindo o perfil NENHUM.
    """
    stmt = select(Profile)
    result = await db.execute(stmt)
    perfis = list(result.scalars().all())

    # Se o perfil EPO GENERALISTA não estiver no banco, inclui virtualmente para alternância no frontend
    if not any(p.id == "EPO_GENERALISTA" or p.tipo == "EPO_GENERALISTA" for p in perfis):
        epo_profile = Profile(
            id="EPO_GENERALISTA",
            nome="EPO GENERALISTA",
            tipo="EPO_GENERALISTA",
            cor="laranja",
            especialidade=None
        )
        perfis.append(epo_profile)

    # Se o perfil NENHUM não estiver no banco, inclui virtualmente para alternância de perfil no frontend
    if not any(p.id == "NENHUM" or p.id == "OBSERVADOR" for p in perfis):
        nenhum_profile = Profile(
            id="NENHUM",
            nome="NENHUM",
            tipo="NENHUM",
            cor="cinza",
            especialidade=None
        )
        perfis.append(nenhum_profile)

    return perfis

@router.post("/ativar")
async def ativar_perfil(
    req: PerfilAtivarRequest,
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    """
    Permite ao usuário ativo alternar seu perfil ativo de trabalho entre seus perfis vinculados (ou qualquer perfil se for ADMIN).
    Retorna um novo token JWT atualizado.
    """
    username = current_user.get("username")
    is_admin = (
        current_user.get("username") == "admin" 
        or current_user.get("is_admin") is True
        or current_user.get("is_admin_user") is True
        or "GLO-SEC-HCPE-SETISD" in current_user.get("groups", [])
        or "GLO-SEC-HCPE-SETISD" in current_user.get("original_groups", [])
        or any(p.get("tipo") == "ADMIN" or p.get("perfil_id") == "ADMIN" for p in current_user.get("available_profiles", []))
    )
    
    # Se ainda não detectou is_admin, consulta se o usuário possui perfil ADMIN na tabela de usuarios
    if not is_admin and username:
        stmt_admin = select(User).where(
            func.lower(User.username) == func.lower(username),
            User.perfil_id == "ADMIN"
        )
        res_admin = await db.execute(stmt_admin)
        if res_admin.scalar_one_or_none():
            is_admin = True

    # Busca o perfil alvo
    stmt = select(Profile).where(Profile.id == req.perfil_id)
    res = await db.execute(stmt)
    target_profile = res.scalar_one_or_none()
    
    if not target_profile and req.perfil_id not in ["NENHUM", "OBSERVADOR", "EPO_GENERALISTA"]:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.")

    # Se não for ADMIN, verifica se o usuário tem este perfil associado na tabela usuarios
    target_user_record = None
    if not is_admin:
        stmt = select(User).where(
            func.lower(User.username) == func.lower(username),
            User.perfil_id == req.perfil_id
        )
        res = await db.execute(stmt)
        target_user_record = res.scalar_one_or_none()
        if not target_user_record and req.perfil_id not in ["NENHUM", "OBSERVADOR"]:
            raise HTTPException(
                status_code=403,
                detail="Você não possui permissão para ativar este perfil."
            )
    else:
        # Se for admin, busca se existe registro específico para a especialidade
        stmt = select(User).where(
            func.lower(User.username) == func.lower(username),
            User.perfil_id == req.perfil_id
        )
        res = await db.execute(stmt)
        target_user_record = res.scalar_one_or_none()

    # Determina os novos atributos do token
    perfil_tipo = target_profile.tipo if target_profile else req.perfil_id
    especialidade = target_profile.especialidade if target_profile else None
    funcao = target_user_record.funcao if target_user_record else current_user.get("funcao")
    
    groups = []
    if perfil_tipo == "ADMIN":
        groups = ["GLO-SEC-HCPE-SETISD", "Users"]
    elif perfil_tipo == "GESTAO_LEC":
        groups = ["GESTAO_LEC", "Users"]
    elif perfil_tipo in ["NENHUM", "OBSERVADOR"]:
        groups = ["NENHUM", "Users"]
    else:
        groups = ["ESPECIALIDADE", "Users"]

    # Se o usuário for ADMIN, preservar o grupo administrativo em groups para que nunca perca o poder de navegação
    if is_admin and "GLO-SEC-HCPE-SETISD" not in groups:
        groups.insert(0, "GLO-SEC-HCPE-SETISD")

    new_user_data = dict(current_user)
    new_user_data["perfil_id"] = req.perfil_id
    new_user_data["perfil_tipo"] = perfil_tipo
    new_user_data["especialidade"] = especialidade
    new_user_data["funcao"] = funcao
    new_user_data["groups"] = groups
    new_user_data["is_admin"] = is_admin
    new_user_data["is_admin_user"] = is_admin
    if "original_groups" not in new_user_data and is_admin:
        new_user_data["original_groups"] = ["GLO-SEC-HCPE-SETISD", "Users"]
    
    new_token = auth_handler.create_access_token(data=new_user_data)
    return {
        "access_token": new_token,
        "token_type": "bearer",
        "user": new_user_data
    }

@router.post("", response_model=PerfilResponse, status_code=status.HTTP_201_CREATED)
async def create_perfil(
    perfil_in: PerfilCreate,
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    """
    Cria um novo perfil do tipo ESPECIALIDADE com cor verde.
    Apenas usuários com perfil ADMIN ou GESTÃO LEC podem criar novos perfis.
    """
    role = get_current_user_role(current_user)
    if role not in ["ADMIN", "GESTAO_LEC"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas usuários ADMIN ou GESTÃO LEC podem criar novos perfis."
        )

    if not perfil_in.especialidade or not perfil_in.especialidade.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A especialidade correspondente é obrigatória para perfis do tipo ESPECIALIDADE."
        )

    spec_name = perfil_in.especialidade.strip().upper()
    norm_spec = remove_accents(spec_name).lower()

    # Busca todos os perfis para validações
    stmt = select(Profile)
    result = await db.execute(stmt)
    all_profiles = list(result.scalars().all())

    # 1. Valida se já existe uma especialidade com mesmo nome (insensível a acentos)
    for p in all_profiles:
        if p.especialidade and remove_accents(p.especialidade).lower() == norm_spec:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe um perfil cadastrado para a especialidade '{spec_name}'."
            )

    # 2. Gera ID limpo e garante unicidade contra colisões
    base_id = generate_profile_id(spec_name)
    candidate_id = base_id
    existing_ids = {p.id for p in all_profiles}
    counter = 2
    while candidate_id in existing_ids:
        candidate_id = f"{base_id}_{counter}"
        counter += 1

    new_profile = Profile(
        id=candidate_id,
        nome=perfil_in.nome.strip().upper(),
        tipo="ESPECIALIDADE",
        cor="verde",
        especialidade=spec_name
    )
    
    db.add(new_profile)

    # Registra evento no Histórico
    await registrar_evento_historico(
        db=db,
        tipo="CRIAR_PERFIL",
        origem_menu="Perfis",
        evento_tipo="EXECUCAO",
        detalhes=f'Perfil "{new_profile.nome}" criado',
        status="CONCLUIDO",
        especialidade=new_profile.especialidade or "—",
        procedimento="—",
        perfil_executor=current_user.get("perfil_tipo") or role,
        usuario=current_user.get("username", "")
    )

    await db.commit()
    await db.refresh(new_profile)
    return new_profile

@router.put("/{perfil_id}", response_model=PerfilResponse)
async def update_perfil(
    perfil_id: str,
    perfil_in: PerfilCreate,
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    """
    Atualiza um perfil existente. Valida as regras hierárquicas.
    """
    role = get_current_user_role(current_user)
    
    # 1. Busca o perfil existente
    stmt = select(Profile).where(Profile.id == perfil_id)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil não encontrado."
        )

    # 2. Validações Hierárquicas de quem está editando
    if role == "ESPECIALIDADE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuários com perfil ESPECIALIDADE não podem editar perfis."
        )
    elif role == "GESTAO_LEC":
        if existing.tipo != "ESPECIALIDADE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuários GESTÃO LEC só podem editar perfis do tipo ESPECIALIDADE."
            )
    elif role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para editar perfis."
        )

    # 3. Validações sobre o novo estado do perfil
    if existing.tipo == "ESPECIALIDADE" and not perfil_in.especialidade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A especialidade correspondente é obrigatória para perfis do tipo ESPECIALIDADE."
        )

    # Se alterou a especialidade, verifica duplicidade
    if existing.tipo == "ESPECIALIDADE" and perfil_in.especialidade:
        new_spec = perfil_in.especialidade.strip().upper()
        norm_new_spec = remove_accents(new_spec).lower()
        
        stmt = select(Profile).where(Profile.id != perfil_id)
        result = await db.execute(stmt)
        other_profiles = result.scalars().all()
        for p in other_profiles:
            if p.especialidade and remove_accents(p.especialidade).lower() == norm_new_spec:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Já existe um perfil cadastrado para a especialidade '{new_spec}'."
                )

    # Atualiza campos
    existing.nome = perfil_in.nome.strip().upper()
    if existing.tipo == "ESPECIALIDADE":
        existing.especialidade = perfil_in.especialidade.strip().upper()

    await db.commit()
    await db.refresh(existing)
    return existing

@router.delete("/{perfil_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_perfil(
    perfil_id: str,
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    """
    Exclui um perfil existente. Valida as regras hierárquicas e associação com usuários.
    """
    role = get_current_user_role(current_user)
    
    # 1. Busca o perfil existente
    stmt = select(Profile).where(Profile.id == perfil_id)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil não encontrado."
        )

    # 2. Validações Hierárquicas
    if role == "ESPECIALIDADE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuários com perfil ESPECIALIDADE não podem excluir perfis."
        )
    elif role == "GESTAO_LEC":
        if existing.tipo != "ESPECIALIDADE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuários GESTÃO LEC só podem excluir perfis do tipo ESPECIALIDADE."
            )
    elif role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para excluir perfis."
        )

    # 3. Verifica associação com usuários
    stmt = select(User).where(User.perfil_id == perfil_id)
    result = await db.execute(stmt)
    associated_user = result.scalar_one_or_none()
    if associated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível excluir um perfil associado a usuários."
        )

    # Registra evento no Histórico
    await registrar_evento_historico(
        db=db,
        tipo="EXCLUIR_PERFIL",
        origem_menu="Perfis",
        evento_tipo="EXECUCAO",
        detalhes=f'Perfil "{existing.nome}" excluído',
        status="CONCLUIDO",
        especialidade=existing.especialidade or "—",
        procedimento="—",
        perfil_executor=current_user.get("perfil_tipo") or role,
        usuario=current_user.get("username", "")
    )

    await db.delete(existing)
    await db.commit()
    return None
