# src/routers/perfil.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..auth.auth import auth_handler
from ..resources.database import get_app_db_session
from ..models.profile import Profile

router = APIRouter(prefix="/api/perfis", tags=["Perfis"])

class PerfilCreate(BaseModel):
    nome: str
    especialidade: Optional[str] = None

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
    elif "ESPECIALIDADE" in groups:
        return "ESPECIALIDADE"
    
    # Se o username for admin, assume ADMIN
    if current_user.get("username") == "admin":
        return "ADMIN"
        
    return "ESPECIALIDADE"  # Default fallback

@router.get("", response_model=List[PerfilResponse])
async def get_perfis(
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    """
    Retorna a lista de todos os perfis cadastrados no banco local.
    """
    stmt = select(Profile)
    result = await db.execute(stmt)
    perfis = result.scalars().all()
    return perfis

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

    if not perfil_in.especialidade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A especialidade correspondente é obrigatória para perfis do tipo ESPECIALIDADE."
        )

    # Verifica se já existe um perfil para esta especialidade
    stmt = select(Profile).where(Profile.especialidade == perfil_in.especialidade)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe um perfil cadastrado para a especialidade {perfil_in.especialidade}."
        )

    # Regras fixas do requisito: tipo ESPECIALIDADE e cor verde
    # ID amigável ou baseado no nome
    perfil_id = perfil_in.especialidade.upper().replace(" ", "_")
    
    new_profile = Profile(
        id=perfil_id,
        nome=perfil_in.nome.upper(),
        tipo="ESPECIALIDADE",
        cor="verde",
        especialidade=perfil_in.especialidade
    )
    
    db.add(new_profile)
    await db.commit()
    await db.refresh(new_profile)
    return new_profile
