# src/routers/usuario.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import hashlib
import os
from datetime import datetime

from ..auth.auth import auth_handler
from ..resources.database import get_app_db_session
from ..models.user import User
from ..models.profile import Profile
from ..models.user_creation_request import UserCreationRequest
from ..helpers.historico_helper import registrar_evento_historico
from .perfil import get_current_user_role

router = APIRouter(prefix="/api/usuarios", tags=["Usuários"])

class UserCreate(BaseModel):
    username: str
    nome: str
    perfil_id: str  # ID do perfil associado
    especialidade: Optional[str] = None  # Relevante se o perfil for Especialidade
    funcao: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    nome: str
    perfil_id: str
    especialidade: Optional[str] = None
    funcao: Optional[str] = None

    class Config:
        from_attributes = True

class UserCreationRequestCreate(BaseModel):
    username: str
    nome: str
    perfil_id: str
    funcao: Optional[str] = None
    tipo: Optional[str] = "CRIACAO"
    user_id: Optional[int] = None
    campos_modificados: Optional[str] = None

class UserCreationRequestResponse(BaseModel):
    id: int
    username: str
    nome: str
    perfil_id: str
    especialidade: Optional[str] = None
    funcao: Optional[str] = None
    status: str
    created_at: datetime
    tipo: str
    user_id: Optional[int] = None
    campos_modificados: Optional[str] = None

    class Config:
        from_attributes = True

def hash_password(password: str) -> str:
    """
    Gera um hash PBKDF2 seguro para a senha.
    """
    salt = os.urandom(16).hex()
    pbkdf2 = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}:{pbkdf2.hex()}"

@router.get("", response_model=List[UserResponse])
async def get_usuarios(
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    """
    Retorna a lista de todos os usuários cadastrados localmente.
    """
    stmt = select(User)
    result = await db.execute(stmt)
    usuarios = result.scalars().all()
    return usuarios

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_usuario(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    """
    Cria um novo usuário local no banco de dados SQLite.
    Valida as regras hierárquicas com base no perfil do criador.
    """
    creator_role = get_current_user_role(current_user)
    creator_specialty = current_user.get("especialidade")

    # Busca o perfil desejado para o novo usuário
    stmt = select(Profile).where(Profile.id == user_in.perfil_id)
    result = await db.execute(stmt)
    target_profile = result.scalar_one_or_none()
    
    if not target_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Perfil especificado não existe."
        )

    if creator_role in ["NENHUM", "OBSERVADOR", "EPO_GENERALISTA"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuários com este perfil não possuem permissão para criar usuários."
        )

    if target_profile.tipo in ["NENHUM", "OBSERVADOR"] or target_profile.id in ["NENHUM", "OBSERVADOR"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é permitido criar usuários com o perfil NENHUM."
        )

    # 1. Validações Hierárquicas
    if target_profile.tipo == "ESPECIALIDADE" and not target_profile.especialidade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Perfis do tipo ESPECIALIDADE devem possuir uma especialidade associada."
        )

    if creator_role == "ESPECIALIDADE":
        # ESPECIALIDADE só pode criar usuários da sua PRÓPRIA especialidade
        if target_profile.tipo != "ESPECIALIDADE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuários com perfil ESPECIALIDADE só podem criar outros usuários do tipo ESPECIALIDADE."
            )
        if target_profile.especialidade != creator_specialty:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Você só pode criar usuários para a sua especialidade ({creator_specialty})."
            )
            
    elif creator_role == "GESTAO_LEC":
        # GESTÃO LEC só pode criar usuários dos perfis GESTÃO LEC ou ESPECIALIDADE (não ADMIN)
        if target_profile.tipo == "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuários GESTÃO LEC não podem criar usuários com perfil ADMIN."
            )
            
    elif creator_role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para criar usuários."
        )

    stmt = select(User).where(
        func.lower(User.username) == func.lower(user_in.username),
        User.perfil_id == user_in.perfil_id
    )
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este usuário já está cadastrado com este perfil."
        )

    # Cria o novo usuário
    new_user = User(
        username=user_in.username,
        nome=user_in.nome,
        perfil_id=user_in.perfil_id,
        especialidade=target_profile.especialidade if target_profile.tipo == "ESPECIALIDADE" else None,
        funcao=user_in.funcao if target_profile.tipo == "ESPECIALIDADE" else None
    )
    
    db.add(new_user)

    # Registra evento no Histórico
    await registrar_evento_historico(
        db=db,
        tipo="CRIAR_USUARIO",
        origem_menu="Usuários",
        evento_tipo="EXECUCAO",
        detalhes=f'Usuário "{new_user.username}" ({new_user.nome}) criado',
        status="CONCLUIDO",
        especialidade=new_user.especialidade or "—",
        procedimento="—",
        perfil_executor=current_user.get("perfil_tipo") or creator_role,
        usuario=current_user.get("username", "")
    )

    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.put("/{user_id}", response_model=UserResponse)
async def update_usuario(
    user_id: int,
    user_in: UserCreate,
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    """
    Atualiza um usuário local. Valida as regras hierárquicas.
    """
    creator_role = get_current_user_role(current_user)
    creator_specialty = current_user.get("especialidade")

    if creator_role in ["NENHUM", "OBSERVADOR", "EPO_GENERALISTA"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para editar usuários."
        )

    # Busca o usuário existente
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_444_NOT_FOUND if hasattr(status, "HTTP_444_NOT_FOUND") else 404,
            detail="Usuário não encontrado."
        )

    # Busca o perfil atual do usuário sendo editado para verificar permissão de edição
    stmt = select(Profile).where(Profile.id == existing_user.perfil_id)
    result = await db.execute(stmt)
    existing_user_profile = result.scalar_one_or_none()

    # Valida se o criador tem permissão sobre o usuário a ser editado
    if existing_user_profile:
        if existing_user_profile.tipo == "ADMIN" and creator_role != "ADMIN":
            raise HTTPException(
                status_code=403,
                detail="Apenas administradores podem editar usuários com perfil ADMIN."
            )
        elif existing_user_profile.tipo == "GESTAO_LEC" and creator_role not in ["ADMIN", "GESTAO_LEC"]:
            raise HTTPException(
                status_code=403,
                detail="Você não tem permissão para editar usuários GESTÃO LEC."
            )
        elif existing_user_profile.tipo == "ESPECIALIDADE" and creator_role == "ESPECIALIDADE":
            if existing_user.especialidade != creator_specialty:
                raise HTTPException(
                    status_code=403,
                    detail=f"Você só tem permissão para editar usuários da sua especialidade ({creator_specialty})."
                )

    # Para perfis ADMIN e GESTÃO LEC, apenas o nome completo pode ser modificado
    is_target_admin_or_gestao = existing_user_profile.tipo in ["ADMIN", "GESTAO_LEC"] if existing_user_profile else False
    if is_target_admin_or_gestao:
        if (
            existing_user.perfil_id != user_in.perfil_id 
            or existing_user.funcao != user_in.funcao
            or existing_user.username != user_in.username
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas o nome completo pode ser alterado para usuários ADMIN e GESTÃO LEC."
            )

    # Busca o novo perfil desejado para o usuário
    stmt = select(Profile).where(Profile.id == user_in.perfil_id)
    result = await db.execute(stmt)
    target_profile = result.scalar_one_or_none()
    
    if not target_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Perfil especificado não existe."
        )

    # Validações Hierárquicas para o novo perfil
    if target_profile.tipo == "ESPECIALIDADE" and not target_profile.especialidade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Perfis do tipo ESPECIALIDADE devem possuir uma especialidade associada."
        )

    if creator_role == "ESPECIALIDADE":
        if target_profile.tipo != "ESPECIALIDADE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuários com perfil ESPECIALIDADE só podem atribuir perfil ESPECIALIDADE."
            )
        if target_profile.especialidade != creator_specialty:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Você só pode atribuir perfis da sua especialidade ({creator_specialty})."
            )
    elif creator_role == "GESTAO_LEC":
        if target_profile.tipo == "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuários GESTÃO LEC não podem atribuir perfil ADMIN."
            )
    elif creator_role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para atualizar usuários."
        )

    # Se alterou username ou perfil_id, verifica duplicidade para (username, perfil_id) em outro registro
    if existing_user.username.lower() != user_in.username.lower() or existing_user.perfil_id != user_in.perfil_id:
        stmt = select(User).where(
            func.lower(User.username) == func.lower(user_in.username),
            User.perfil_id == user_in.perfil_id,
            User.id != user_id
        )
        result = await db.execute(stmt)
        duplicate_user = result.scalar_one_or_none()
        if duplicate_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um cadastro deste usuário com este perfil."
            )

    # Rastreia campos modificados
    diffs = []
    if existing_user.nome != user_in.nome:
        diffs.append(f"Nome: {existing_user.nome} -> {user_in.nome}")
    if existing_user.perfil_id != user_in.perfil_id:
        diffs.append(f"Perfil: {existing_user.perfil_id} -> {user_in.perfil_id}")
    new_spec = target_profile.especialidade if target_profile.tipo == "ESPECIALIDADE" else None
    if existing_user.especialidade != new_spec:
        diffs.append(f"Especialidade: {existing_user.especialidade or '—'} -> {new_spec or '—'}")
    new_func = user_in.funcao if target_profile.tipo == "ESPECIALIDADE" else None
    if existing_user.funcao != new_func:
        diffs.append(f"Função: {existing_user.funcao or '—'} -> {new_func or '—'}")

    # Atualiza
    existing_user.username = user_in.username
    existing_user.nome = user_in.nome
    existing_user.perfil_id = user_in.perfil_id
    existing_user.especialidade = new_spec
    existing_user.funcao = new_func

    # Registra evento no Histórico
    detalhes_historico = f'Usuário "{existing_user.username}" ({existing_user.nome}) editado'
    if diffs:
        detalhes_historico += f' - {"; ".join(diffs)}'

    await registrar_evento_historico(
        db=db,
        tipo="EDITAR_USUARIO",
        origem_menu="Usuários",
        evento_tipo="EXECUCAO",
        detalhes=detalhes_historico,
        status="CONCLUIDO",
        especialidade=existing_user.especialidade or "—",
        procedimento="—",
        perfil_executor=current_user.get("perfil_tipo") or creator_role,
        usuario=current_user.get("username", "")
    )

    await db.commit()
    await db.refresh(existing_user)
    return existing_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(
    user_id: int,
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    """
    Exclui um usuário local. Valida as regras hierárquicas.
    """
    creator_role = get_current_user_role(current_user)
    creator_specialty = current_user.get("especialidade")

    if creator_role in ["NENHUM", "OBSERVADOR", "EPO_GENERALISTA"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para excluir usuários."
        )

    # Busca o usuário existente
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )

    # Busca o perfil do usuário
    stmt = select(Profile).where(Profile.id == existing_user.perfil_id)
    result = await db.execute(stmt)
    user_profile = result.scalar_one_or_none()

    # Validações Hierárquicas para exclusão
    if user_profile:
        if user_profile.tipo == "ADMIN" and creator_role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem excluir usuários com perfil ADMIN."
            )
        if creator_role == "GESTAO_LEC" and user_profile.tipo != "ESPECIALIDADE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuários GESTÃO LEC só podem excluir usuários do tipo ESPECIALIDADE."
            )
        if creator_role == "ESPECIALIDADE":
            if user_profile.tipo != "ESPECIALIDADE" or user_profile.especialidade != creator_specialty:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Você só tem permissão para excluir usuários da sua especialidade ({creator_specialty})."
                )
    elif creator_role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para excluir usuários."
        )

    # Registra evento no Histórico
    await registrar_evento_historico(
        db=db,
        tipo="EXCLUIR_USUARIO",
        origem_menu="Usuários",
        evento_tipo="EXECUCAO",
        detalhes=f'Usuário "{existing_user.username}" ({existing_user.nome}) excluído',
        status="CONCLUIDO",
        especialidade=existing_user.especialidade or "—",
        procedimento="—",
        perfil_executor=current_user.get("perfil_tipo") or creator_role,
        usuario=current_user.get("username", "")
    )

    await db.delete(existing_user)
    await db.commit()
    return None

@router.get("/solicitacoes", response_model=List[UserCreationRequestResponse])
async def get_solicitacoes(
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    """
    Retorna a lista de todas as solicitações de criação de usuário pendentes (apenas ADMIN e GESTÃO LEC).
    """
    creator_role = get_current_user_role(current_user)
    if creator_role not in ["ADMIN", "GESTAO_LEC"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas ADMIN e GESTÃO LEC podem visualizar solicitações de criação."
        )
    
    stmt = select(UserCreationRequest).where(UserCreationRequest.status == "PENDENTE").order_by(UserCreationRequest.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/solicitacoes/count")
async def get_solicitacoes_count(
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    """
    Retorna a contagem de solicitações pendentes.
    """
    stmt = select(func.count(UserCreationRequest.id)).where(UserCreationRequest.status == "PENDENTE")
    result = await db.execute(stmt)
    count = result.scalar() or 0
    return {"count": count}

@router.post("/solicitacoes", response_model=UserCreationRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_solicitacao(
    req_in: UserCreationRequestCreate,
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    """
    Cria uma nova solicitação de criação ou edição de usuário.
    Usuários com perfil ESPECIALIDADE só podem solicitar para sua própria especialidade.
    """
    creator_role = get_current_user_role(current_user)
    creator_specialty = current_user.get("especialidade")

    # Verifica se o perfil de acesso solicitado existe
    stmt = select(Profile).where(Profile.id == req_in.perfil_id)
    result = await db.execute(stmt)
    target_profile = result.scalar_one_or_none()
    if not target_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Perfil especificado não existe."
        )

    if creator_role in ["NENHUM", "OBSERVADOR", "EPO_GENERALISTA"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuários com este perfil não possuem permissão para solicitar ações de usuários."
        )

    if target_profile.tipo in ["NENHUM", "OBSERVADOR"] or target_profile.id in ["NENHUM", "OBSERVADOR"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é permitido solicitar a criação de usuários com o perfil NENHUM."
        )

    # Regras de validação do perfil solicitado
    if target_profile.tipo == "ESPECIALIDADE" and not target_profile.especialidade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Perfis do tipo ESPECIALIDADE devem possuir uma especialidade associada."
        )

    # Validações baseadas no criador
    if creator_role == "ESPECIALIDADE":
        # Deve ser para a sua especialidade
        if target_profile.tipo != "ESPECIALIDADE" or target_profile.especialidade != creator_specialty:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Você só pode solicitar ações para a sua especialidade ({creator_specialty})."
            )
    elif creator_role == "GESTAO_LEC":
        if target_profile.tipo == "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuários GESTÃO LEC não podem solicitar perfil ADMIN."
            )

    is_edition = req_in.tipo == "EDICAO"
    is_deletion = req_in.tipo == "EXCLUSAO"

    if is_edition or is_deletion:
        if not req_in.user_id:
            action_name = "exclusão" if is_deletion else "edição"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ID do usuário é obrigatório para solicitações de {action_name}."
            )
        # Busca o usuário existente
        stmt = select(User).where(User.id == req_in.user_id)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        if not existing_user:
            action_name = "excluído" if is_deletion else "editado"
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário a ser {action_name} não encontrado."
            )
        
        if is_edition:
            # O campo usuário Ebserh (username) não pode ser modificado
            if existing_user.username.lower() != req_in.username.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="O usuário Ebserh não pode ser modificado."
                )

        # Valida se o criador tem permissão sobre o usuário a ser editado/excluído
        stmt = select(Profile).where(Profile.id == existing_user.perfil_id)
        result = await db.execute(stmt)
        existing_user_profile = result.scalar_one_or_none()
        if existing_user_profile:
            action_name = "exclusão" if is_deletion else "edição"
            if existing_user_profile.tipo == "ADMIN" and creator_role != "ADMIN":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Apenas administradores podem solicitar {action_name} de usuários com perfil ADMIN."
                )
            if creator_role == "GESTAO_LEC" and existing_user_profile.tipo != "ESPECIALIDADE":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Usuários GESTÃO LEC só podem solicitar {action_name} de usuários do tipo ESPECIALIDADE."
                )
            if creator_role == "ESPECIALIDADE":
                if existing_user_profile.tipo != "ESPECIALIDADE" or existing_user_profile.especialidade != creator_specialty:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Você só tem permissão para solicitar {action_name} de usuários da sua especialidade ({creator_specialty})."
                    )
    else:
        # Verifica se o username já está cadastrado localmente para novos usuários COM O MESMO PERFIL
        stmt = select(User).where(
            func.lower(User.username) == func.lower(req_in.username),
            User.perfil_id == req_in.perfil_id
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este usuário já está cadastrado com este perfil no sistema."
            )

    # Verifica se já existe solicitação pendente para este nome de usuário COM ESTE PERFIL
    stmt = select(UserCreationRequest).where(
        func.lower(UserCreationRequest.username) == func.lower(req_in.username),
        UserCreationRequest.perfil_id == req_in.perfil_id,
        UserCreationRequest.status == "PENDENTE"
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma solicitação pendente para este usuário com este perfil."
        )

    new_request = UserCreationRequest(
        username=req_in.username.strip(),
        nome=req_in.nome.strip(),
        perfil_id=req_in.perfil_id,
        especialidade=target_profile.especialidade if target_profile.tipo == "ESPECIALIDADE" else None,
        funcao=req_in.funcao if target_profile.tipo == "ESPECIALIDADE" else None,
        status="PENDENTE",
        created_at=datetime.utcnow(),
        tipo=req_in.tipo or "CRIACAO",
        user_id=req_in.user_id,
        campos_modificados=req_in.campos_modificados
    )

    db.add(new_request)

    # Registra evento no Histórico
    is_del = (req_in.tipo or "").upper() == "EXCLUSAO"
    is_ed = (req_in.tipo or "").upper() == "EDICAO"
    action_code = "EXCLUIR_USUARIO" if is_del else ("EDITAR_USUARIO" if is_ed else "CRIAR_USUARIO")
    action_desc = "exclusão" if is_del else ("edição" if is_ed else "criação")

    detalhes_solic = f'Solicitada {action_desc} do usuário "{req_in.username}" ({req_in.nome})'
    if is_ed and req_in.campos_modificados:
        detalhes_solic += f' - Alterações: {req_in.campos_modificados}'

    await registrar_evento_historico(
        db=db,
        tipo=action_code,
        origem_menu="Usuários",
        evento_tipo="SOLICITACAO",
        detalhes=detalhes_solic,
        status="PENDENTE",
        especialidade=target_profile.especialidade if target_profile.tipo == "ESPECIALIDADE" else "—",
        procedimento="—",
        perfil_executor=current_user.get("perfil_tipo") or creator_role,
        usuario=current_user.get("username", "")
    )

    await db.commit()
    await db.refresh(new_request)
    return new_request

@router.post("/solicitacoes/{id}/aprovar", response_model=UserResponse)
async def aprovar_solicitacao(
    id: int,
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    """
    Aprova uma solicitação de criação de usuário pendente. Cria o usuário real.
    """
    creator_role = get_current_user_role(current_user)
    if creator_role not in ["ADMIN", "GESTAO_LEC"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas ADMIN e GESTÃO LEC podem aprovar solicitações."
        )

    stmt = select(UserCreationRequest).where(UserCreationRequest.id == id)
    result = await db.execute(stmt)
    request_obj = result.scalar_one_or_none()
    if not request_obj or request_obj.status != "PENDENTE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solicitação não encontrada ou não está pendente."
        )

    # Se for GESTÃO LEC, só pode aprovar solicitações de perfis do tipo Especialidade
    stmt = select(Profile).where(Profile.id == request_obj.perfil_id)
    result = await db.execute(stmt)
    target_profile = result.scalar_one_or_none()
    
    if creator_role == "GESTAO_LEC" and (not target_profile or target_profile.tipo != "ESPECIALIDADE"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuários GESTÃO LEC apenas podem aprovar solicitações de perfis ESPECIALIDADE."
        )

    # Se a solicitação for de exclusão, excluímos o usuário existente
    if request_obj.tipo == "EXCLUSAO":
        stmt = select(User).where(User.id == request_obj.user_id)
        result = await db.execute(stmt)
        user_to_delete = result.scalar_one_or_none()
        
        deleted_resp = None
        if user_to_delete:
            deleted_resp = UserResponse(
                id=user_to_delete.id,
                username=user_to_delete.username,
                nome=user_to_delete.nome,
                perfil_id=user_to_delete.perfil_id,
                especialidade=user_to_delete.especialidade,
                funcao=user_to_delete.funcao
            )
            await db.delete(user_to_delete)
        else:
            deleted_resp = UserResponse(
                id=request_obj.user_id or 0,
                username=request_obj.username,
                nome=request_obj.nome,
                perfil_id=request_obj.perfil_id,
                especialidade=request_obj.especialidade,
                funcao=request_obj.funcao
            )

        request_obj.status = "APROVADO"
        # Registra evento no Histórico
        await registrar_evento_historico(
            db=db,
            tipo="EXCLUIR_USUARIO",
            origem_menu="Usuários",
            evento_tipo="RESPOSTA",
            detalhes=f'Exclusão do usuário "{request_obj.username}" ({request_obj.nome}) aprovada',
            status="APROVADO",
            especialidade=request_obj.especialidade or "—",
            procedimento="—",
            perfil_executor=current_user.get("perfil_tipo") or creator_role,
            usuario=current_user.get("username", "")
        )
        await db.commit()
        return deleted_resp

    # Se a solicitação for de edição, atualizamos o usuário existente
    if request_obj.tipo == "EDICAO":
        stmt = select(User).where(User.id == request_obj.user_id)
        result = await db.execute(stmt)
        user_to_edit = result.scalar_one_or_none()
        if not user_to_edit:
            request_obj.status = "REJEITADO"
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário a ser editado não existe. Solicitação rejeitada automaticamente."
            )
        
        user_to_edit.nome = request_obj.nome
        user_to_edit.perfil_id = request_obj.perfil_id
        user_to_edit.especialidade = request_obj.especialidade
        user_to_edit.funcao = request_obj.funcao

        request_obj.status = "APROVADO"
        # Registra evento no Histórico
        detalhes_aprov = f'Edição do usuário "{request_obj.username}" ({request_obj.nome}) aprovada'
        if request_obj.campos_modificados:
            detalhes_aprov += f' - Alterações: {request_obj.campos_modificados}'
        await registrar_evento_historico(
            db=db,
            tipo="EDITAR_USUARIO",
            origem_menu="Usuários",
            evento_tipo="RESPOSTA",
            detalhes=detalhes_aprov,
            status="APROVADO",
            especialidade=request_obj.especialidade or "—",
            procedimento="—",
            perfil_executor=current_user.get("perfil_tipo") or creator_role,
            usuario=current_user.get("username", "")
        )
        await db.commit()
        await db.refresh(user_to_edit)
        return user_to_edit

    # Para solicitações de criação (CRIACAO), mantém o fluxo original
    # Verifica duplicidade novamente antes de inserir
    stmt = select(User).where(
        func.lower(User.username) == func.lower(request_obj.username),
        User.perfil_id == request_obj.perfil_id
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        request_obj.status = "REJEITADO"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já cadastrado com este perfil anteriormente. Solicitação rejeitada automaticamente."
        )

    # Cria o usuário real
    new_user = User(
        username=request_obj.username,
        nome=request_obj.nome,
        perfil_id=request_obj.perfil_id,
        especialidade=request_obj.especialidade,
        funcao=request_obj.funcao
    )
    db.add(new_user)
    
    # Atualiza status da solicitação
    request_obj.status = "APROVADO"
    # Registra evento no Histórico
    await registrar_evento_historico(
        db=db,
        tipo="CRIAR_USUARIO",
        origem_menu="Usuários",
        evento_tipo="RESPOSTA",
        detalhes=f'Criação do usuário "{request_obj.username}" ({request_obj.nome}) aprovada',
        status="APROVADO",
        especialidade=request_obj.especialidade or "—",
        procedimento="—",
        perfil_executor=current_user.get("perfil_tipo") or creator_role,
        usuario=current_user.get("username", "")
    )
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/solicitacoes/{id}/rejeitar", response_model=UserCreationRequestResponse)
async def rejeitar_solicitacao(
    id: int,
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    """
    Rejeita uma solicitação de criação de usuário pendente.
    """
    creator_role = get_current_user_role(current_user)
    if creator_role not in ["ADMIN", "GESTAO_LEC"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas ADMIN e GESTÃO LEC podem rejeitar solicitações."
        )

    stmt = select(UserCreationRequest).where(UserCreationRequest.id == id)
    result = await db.execute(stmt)
    request_obj = result.scalar_one_or_none()
    if not request_obj or request_obj.status != "PENDENTE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solicitação não encontrada ou não está pendente."
        )

    # Se for GESTÃO LEC, só pode rejeitar solicitações de perfis do tipo Especialidade
    stmt = select(Profile).where(Profile.id == request_obj.perfil_id)
    result = await db.execute(stmt)
    target_profile = result.scalar_one_or_none()
    
    if creator_role == "GESTAO_LEC" and (not target_profile or target_profile.tipo != "ESPECIALIDADE"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuários GESTÃO LEC apenas podem rejeitar solicitações de perfis ESPECIALIDADE."
        )

    request_obj.status = "REJEITADO"
    
    is_del = request_obj.tipo == "EXCLUSAO"
    is_ed = request_obj.tipo == "EDICAO"
    action_code = "EXCLUIR_USUARIO" if is_del else ("EDITAR_USUARIO" if is_ed else "CRIAR_USUARIO")
    action_desc = "Exclusão" if is_del else ("Edição" if is_ed else "Criação")

    # Registra evento no Histórico
    await registrar_evento_historico(
        db=db,
        tipo=action_code,
        origem_menu="Usuários",
        evento_tipo="RESPOSTA",
        detalhes=f'{action_desc} do usuário "{request_obj.username}" ({request_obj.nome}) rejeitada',
        status="REJEITADO",
        especialidade=request_obj.especialidade or "—",
        procedimento="—",
        perfil_executor=current_user.get("perfil_tipo") or creator_role,
        usuario=current_user.get("username", "")
    )

    await db.commit()
    await db.refresh(request_obj)
    return request_obj
