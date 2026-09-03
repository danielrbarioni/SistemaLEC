from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import HTTPException, status

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

        found_map = {}
        if self.postgres:
            try:
                from sqlalchemy import text
                query = text("""
                    SELECT prontuario as codigo, nome, dt_nascimento, nome_mae 
                    FROM agh.aip_pacientes 
                    WHERE prontuario = ANY(:codigos)
                """)
                res = await self.postgres.session.execute(query, {"codigos": list(list_codigos)})
                for row in res.mappings().all():
                    found_map[row["codigo"]] = dict(row)
            except Exception as e:
                print(f"Erro ao obter dados dos pacientes do AGHU: {e}. Executando fallback para SQLite local.")

        # Complementa os pacientes que não foram encontrados no AGHU com os dados do SQLite local
        missing_codigos = [c for c in list_codigos if c not in found_map]
        if missing_codigos:
            try:
                from ...models.paciente import Paciente
                stmt = select(Paciente).where(Paciente.codigo.in_(missing_codigos))
                res = await self.sqlite.session.execute(stmt)
                rows = res.scalars().all()
                for p in rows:
                    found_map[p.codigo] = {
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
                        "ultima_consulta_epo": p.ultima_consulta_epo,
                        "categorizacao": getattr(p, "categorizacao", "") or "",
                        "lateralidade": getattr(p, "lateralidade", "Indefinida") or "Indefinida"
                    }
            except Exception as e:
                print(f"Erro ao obter dados dos pacientes do SQLite: {e}")

        # Garante que todos os pacientes retornados contenham categorizacao e lateralidade atualizadas do SQLite local
        try:
            from ...models.paciente import Paciente
            stmt_all = select(Paciente).where(Paciente.codigo.in_(list(found_map.keys())))
            res_all = await self.sqlite.session.execute(stmt_all)
            pacientes_db = {p.codigo: p for p in res_all.scalars().all()}
            
            for cod, p_dict in found_map.items():
                p_db = pacientes_db.get(cod)
                p_dict["categorizacao"] = (getattr(p_db, "categorizacao", "") or "") if p_db else (p_dict.get("categorizacao") or "")
                p_dict["lateralidade"] = (getattr(p_db, "lateralidade", "Indefinida") or "Indefinida") if p_db else (p_dict.get("lateralidade") or "Indefinida")
        except Exception as e:
            print(f"Erro ao enriquecer dados do SQLite local: {e}")
            for p_dict in found_map.values():
                p_dict.setdefault("categorizacao", "")
                p_dict.setdefault("lateralidade", "Indefinida")

        return list(found_map.values())

    async def obter_paciente_por_codigo(self, codigo: int) -> Dict[str, Any]:
        pac_data = None
        if self.postgres:
            try:
                pac_data = await self.postgres.obter_paciente_por_codigo(codigo)
            except HTTPException as e:
                # Se não encontrado no AGHU (404), verifica no SQLite local antes de falhar
                if e.status_code != status.HTTP_404_NOT_FOUND:
                    raise e
            except Exception as e:
                print(f"Erro ao obter paciente {codigo} do AGHU: {e}. Executando fallback para SQLite local.")
        
        if not pac_data:
            pac_data = await self.sqlite.obter_paciente_por_codigo(codigo)

        # Enriquece com dados do SQLite local
        try:
            from ...models.paciente import Paciente
            stmt = select(Paciente).where(Paciente.codigo == codigo)
            res = await self.sqlite.session.execute(stmt)
            p_db = res.scalars().first()
            if p_db:
                pac_data["categorizacao"] = getattr(p_db, "categorizacao", "") or ""
                pac_data["lateralidade"] = getattr(p_db, "lateralidade", "Indefinida") or "Indefinida"
            else:
                pac_data.setdefault("categorizacao", "")
                pac_data.setdefault("lateralidade", "Indefinida")
        except Exception:
            pac_data.setdefault("categorizacao", "")
            pac_data.setdefault("lateralidade", "Indefinida")

        return pac_data

    async def obter_procedimentos_por_especialidade(self, id_especialidade: int) -> List[Dict[str, Any]]:
        if self.postgres:
            try:
                return await self.postgres.obter_procedimentos_por_especialidade(id_especialidade)
            except Exception as e:
                print(f"Erro ao obter procedimentos da especialidade {id_especialidade} do AGHU: {e}. Retornando lista vazia.")
        return await self.sqlite.obter_procedimentos_por_especialidade(id_especialidade)
