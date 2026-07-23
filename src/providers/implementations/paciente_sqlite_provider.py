from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from ..interfaces.paciente_provider_interface import PacienteProviderInterface
from ...models.paciente import Paciente

class PacienteSqliteProvider(PacienteProviderInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar_pacientes(self) -> List[Dict[str, Any]]:
        stmt = select(Paciente)
        result = await self.session.execute(stmt)
        pacientes = result.scalars().all()
        
        return [
            {
                "codigo": p.codigo,
                "nome": p.nome,
                "dt_nascimento": p.dt_nascimento,
                "cpf": p.cpf,
                "sexo": p.sexo,
                "cor": p.cor,
                "nome_mae": p.nome_mae,
                "nome_pai": p.nome_pai,
                "data_hora_inicio": p.data_hora_inicio,
                "status_consulta": p.status_consulta,
                "especialidade": p.especialidade,
                "procedimento": p.procedimento,
                "ultima_consulta_epo": p.ultima_consulta_epo
            }
            for p in pacientes
        ]

    async def obter_paciente_por_codigo(self, codigo: int) -> Dict[str, Any]:
        stmt = select(Paciente).where(Paciente.codigo == codigo)
        result = await self.session.execute(stmt)
        p = result.scalar_one_or_none()
        
        if not p:
            return {
                "codigo": codigo,
                "nome": f"Paciente #{codigo}",
                "dt_nascimento": "—",
                "cpf": None,
                "sexo": None,
                "cor": None,
                "nome_mae": "—",
                "nome_pai": None,
                "data_hora_inicio": None,
                "status_consulta": None,
                "especialidade": None,
                "procedimento": None,
                "ultima_consulta_epo": None
            }
            
        return {
            "codigo": p.codigo,
            "nome": p.nome,
            "dt_nascimento": p.dt_nascimento,
            "cpf": p.cpf,
            "sexo": p.sexo,
            "cor": p.cor,
            "nome_mae": p.nome_mae,
            "nome_pai": p.nome_pai,
            "data_hora_inicio": p.data_hora_inicio,
            "status_consulta": p.status_consulta,
            "especialidade": p.especialidade,
            "procedimento": p.procedimento,
            "ultima_consulta_epo": p.ultima_consulta_epo
        }

    async def obter_procedimentos_por_especialidade(self, id_especialidade: int) -> List[Dict[str, Any]]:
        # O SQLite local não gerencia a tabela de especialidades/procedimentos cirúrgicos do AGHU
        return []
