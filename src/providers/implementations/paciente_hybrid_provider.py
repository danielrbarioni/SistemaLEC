import time
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import HTTPException, status

from ..interfaces.paciente_provider_interface import PacienteProviderInterface
from .paciente_postgres_provider import PacientePostgresProvider
from .paciente_sqlite_provider import PacienteSqliteProvider
from ...models.solicitacao import Solicitacao
from ...models.status_local import StatusLocal
from ...helpers.string_helper import aplicar_nome_social_dict

# Cache em memória para evitar sobrecarga de consultas repetitivas ao AGHU e SQLite em alta concorrência
_AGHU_PACIENTES_CACHE: Dict[int, Dict[str, Any]] = {}
_AGHU_CACHE_TIMESTAMP: float = 0.0
_AGHU_CACHE_TTL_SECONDS: float = 300.0  # 5 minutos para dados cadastrais do AGHU

_LISTAR_PACIENTES_CACHE: Optional[List[Dict[str, Any]]] = None
_LISTAR_CACHE_TIMESTAMP: float = 0.0
_LISTAR_CACHE_TTL_SECONDS: float = 15.0  # 15 segundos para listagem consolidada

_SOLICITACOES_JSON_CACHE: Optional[bytes] = None
_SOLICITACOES_CACHE_TIMESTAMP: float = 0.0
_SOLICITACOES_CACHE_TTL_SECONDS: float = 10.0  # 10 segundos para JSON de solicitações


def invalidate_paciente_cache() -> None:
    """Invalida o cache da listagem consolidada de pacientes e solicitações após alterações."""
    global _LISTAR_PACIENTES_CACHE, _LISTAR_CACHE_TIMESTAMP
    global _SOLICITACOES_JSON_CACHE, _SOLICITACOES_CACHE_TIMESTAMP
    _LISTAR_PACIENTES_CACHE = None
    _LISTAR_CACHE_TIMESTAMP = 0.0
    _SOLICITACOES_JSON_CACHE = None
    _SOLICITACOES_CACHE_TIMESTAMP = 0.0


def get_solicitacoes_json_cache() -> Optional[bytes]:
    if _SOLICITACOES_JSON_CACHE is not None and (time.monotonic() - _SOLICITACOES_CACHE_TIMESTAMP) < _SOLICITACOES_CACHE_TTL_SECONDS:
        return _SOLICITACOES_JSON_CACHE
    return None


def set_solicitacoes_json_cache(data_bytes: bytes) -> None:
    global _SOLICITACOES_JSON_CACHE, _SOLICITACOES_CACHE_TIMESTAMP
    _SOLICITACOES_JSON_CACHE = data_bytes
    _SOLICITACOES_CACHE_TIMESTAMP = time.monotonic()


class HybridPacienteProvider(PacienteProviderInterface):
    def __init__(self, postgres_session: AsyncSession, sqlite_session: AsyncSession):
        self.postgres = PacientePostgresProvider(session=postgres_session) if postgres_session else None
        self.sqlite = PacienteSqliteProvider(session=sqlite_session)

    def _is_mock_session(self) -> bool:
        return "Mock" in type(self.sqlite.session).__name__

    async def listar_pacientes(self) -> List[Dict[str, Any]]:
        global _AGHU_PACIENTES_CACHE, _AGHU_CACHE_TIMESTAMP
        global _LISTAR_PACIENTES_CACHE, _LISTAR_CACHE_TIMESTAMP

        use_cache = not self._is_mock_session() and self.postgres is not None
        now = time.monotonic()

        if use_cache and _LISTAR_PACIENTES_CACHE is not None and (now - _LISTAR_CACHE_TIMESTAMP) < _LISTAR_CACHE_TTL_SECONDS:
            return _LISTAR_PACIENTES_CACHE

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

        found_map: Dict[Any, Dict[str, Any]] = {}
        if self.postgres:
            try:
                from sqlalchemy import text

                if use_cache:
                    # Se o cache do AGHU expirou, limpa para recarregar
                    if (now - _AGHU_CACHE_TIMESTAMP) >= _AGHU_CACHE_TTL_SECONDS:
                        _AGHU_PACIENTES_CACHE.clear()
                        _AGHU_CACHE_TIMESTAMP = now

                    codigos_para_buscar = [c for c in list_codigos if c not in _AGHU_PACIENTES_CACHE]
                else:
                    codigos_para_buscar = list(list_codigos)

                if codigos_para_buscar:
                    query = text("""
                        SELECT prontuario as codigo, nome, nome_social, dt_nascimento, nome_mae 
                        FROM agh.aip_pacientes 
                        WHERE prontuario = ANY(:codigos)
                    """)
                    res = await self.postgres.session.execute(query, {"codigos": codigos_para_buscar})
                    for row in res.mappings().all():
                        pac_dict = aplicar_nome_social_dict(dict(row))
                        if use_cache:
                            _AGHU_PACIENTES_CACHE[row["codigo"]] = pac_dict
                        else:
                            found_map[row["codigo"]] = pac_dict

                if use_cache:
                    for c in list_codigos:
                        cached_p = _AGHU_PACIENTES_CACHE.get(c)
                        if cached_p is not None:
                            found_map[c] = dict(cached_p)
            except Exception as e:
                print(f"Erro ao obter dados dos pacientes do AGHU: {e}. Executando fallback para SQLite local.")

        # 2. Carrega dados locais do SQLite em uma única consulta (evitando cláusulas IN com milhares de parâmetros)
        pacientes_db: Dict[Any, Any] = {}
        try:
            from ...models.paciente import Paciente
            if len(list_codigos) > 500:
                stmt_local = select(Paciente)
            else:
                stmt_local = select(Paciente).where(Paciente.codigo.in_(list_codigos))
            res_local = await self.sqlite.session.execute(stmt_local)
            for p in res_local.scalars().all():
                pacientes_db[p.codigo] = p
        except Exception as e:
            print(f"Erro ao obter dados dos pacientes do SQLite: {e}")

        # Complementa pacientes que não foram encontrados no AGHU com os dados do SQLite local
        for c in list_codigos:
            if c not in found_map and c in pacientes_db:
                p = pacientes_db[c]
                found_map[p.codigo] = aplicar_nome_social_dict({
                    "codigo": p.codigo,
                    "nome": p.nome,
                    "nome_social": getattr(p, "nome_social", None),
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
                })

        # Garante que todos os pacientes retornados contenham categorizacao e lateralidade atualizadas do SQLite local
        for cod, p_dict in found_map.items():
            p_db = pacientes_db.get(cod)
            p_dict["categorizacao"] = (getattr(p_db, "categorizacao", "") or "") if p_db else (p_dict.get("categorizacao") or "")
            p_dict["lateralidade"] = (getattr(p_db, "lateralidade", "Indefinida") or "Indefinida") if p_db else (p_dict.get("lateralidade") or "Indefinida")

        result_list = list(found_map.values())
        if use_cache:
            _LISTAR_PACIENTES_CACHE = result_list
            _LISTAR_CACHE_TIMESTAMP = time.monotonic()

        return result_list

    async def obter_paciente_por_codigo(self, codigo: int) -> Dict[str, Any]:
        pac_data = None
        if self.postgres:
            try:
                pac_data = await self.postgres.obter_paciente_por_codigo(codigo)
                if pac_data and not self._is_mock_session():
                    _AGHU_PACIENTES_CACHE[codigo] = dict(pac_data)
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
