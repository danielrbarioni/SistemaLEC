from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..interfaces.paciente_provider_interface import PacienteProviderInterface
from .paciente_postgres_provider import PacientePostgresProvider
from .paciente_sqlite_provider import PacienteSqliteProvider
from ...models.solicitacao import Solicitacao
from ...models.status_local import StatusLocal

class HybridPacienteProvider(PacienteProviderInterface):
    def __init__(self, postgres_session: AsyncSession, sqlite_session: AsyncSession):
        self.postgres = PacientePostgresProvider(session=postgres_session) if postgres_session else None
        self.sqlite = PacienteSqliteProvider(session=sqlite_session)

    async def listar_pacientes(self) -> List[Dict[str, Any]]:
        # 1. Busca os códigos de paciente que possuem alguma solicitação ou status local no LEC
        try:
            stmt_solics = select(Solicitacao.codigo_paciente).distinct()
            res_solics = await self.sqlite.session.execute(stmt_solics)
            codigos = {row[0] for row in res_solics.all() if row[0] is not None}

            stmt_status = select(StatusLocal.codigo_paciente).distinct()
            res_status = await self.sqlite.session.execute(stmt_status)
            codigos.update(row[0] for row in res_status.all() if row[0] is not None)
            
            list_codigos = list(codigos)
        except Exception as e:
            print(f"Erro ao buscar códigos de paciente ativos no SQLite: {e}")
            list_codigos = []

        if not list_codigos:
            return []

        # 2. Busca os dados cadastrais (nome, nascimento, mãe) apenas desses pacientes
        if self.postgres:
            try:
                from sqlalchemy import text
                query = text("""
                    SELECT prontuario as codigo, nome, dt_nascimento, nome_mae 
                    FROM agh.aip_pacientes 
                    WHERE prontuario = ANY(:codigos)
                """)
                res = await self.postgres.session.execute(query, {"codigos": list(list_codigos)})
                return [dict(row) for row in res.mappings().all()]
            except Exception as e:
                print(f"Erro ao obter dados dos pacientes do AGHU: {e}. Executando fallback para SQLite local.")

        try:
            from ...models.paciente import Paciente
            stmt = select(Paciente).where(Paciente.codigo.in_(list_codigos))
            res = await self.sqlite.session.execute(stmt)
            rows = res.scalars().all()
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
                for p in rows
            ]
        except Exception as e:
            print(f"Erro ao obter dados dos pacientes do SQLite: {e}")
            return []

    async def obter_paciente_por_codigo(self, codigo: int) -> Dict[str, Any]:
        if self.postgres:
            try:
                return await self.postgres.obter_paciente_por_codigo(codigo)
            except Exception as e:
                print(f"Erro ao obter paciente {codigo} do AGHU: {e}. Executando fallback para SQLite local.")
        return await self.sqlite.obter_paciente_por_codigo(codigo)

    async def obter_procedimentos_por_especialidade(self, id_especialidade: int) -> List[Dict[str, Any]]:
        if self.postgres:
            try:
                return await self.postgres.obter_procedimentos_por_especialidade(id_especialidade)
            except Exception as e:
                print(f"Erro ao obter procedimentos da especialidade {id_especialidade} do AGHU: {e}. Retornando lista vazia.")
        return await self.sqlite.obter_procedimentos_por_especialidade(id_especialidade)
