# src/routers/usuario.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import hashlib
import os

from ..auth.auth import auth_handler
from ..resources.database import get_app_db_session
from ..models.user import User
from ..models.profile import Profile
from .perfil import get_current_user_role

router = APIRouter(prefix="/api/usuarios", tags=["Usuários"])

class UserCreate(BaseModel):
    username: str
    nome: str
    perfil_id: str  # ID do perfil associado
    especialidade: Optional[str] = None  # Relevante se o perfil for Especialidade

class UserResponse(BaseModel):
    id: int
    username: str
    nome: str
    perfil_id: str
    especialidade: Optional[str] = None

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

    stmt = select(User).where(func.lower(User.username) == func.lower(user_in.username))
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de usuário já cadastrado."
        )

    # Cria o novo usuário
    new_user = User(
        username=user_in.username,
        nome=user_in.nome,
        perfil_id=user_in.perfil_id,
        especialidade=target_profile.especialidade if target_profile.tipo == "ESPECIALIDADE" else None
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
