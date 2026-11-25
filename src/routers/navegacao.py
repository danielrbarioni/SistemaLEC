import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.auth import auth_handler
from ..helpers.string_helper import aplicar_nome_social_dict
from ..models.navegacao_config import NavegacaoConfig
from ..resources.database import get_aghu_db_session, get_app_db_session

router = APIRouter(
    prefix="/api/navegacao",
    tags=["Navegacao"],
    dependencies=[Depends(auth_handler.decode_token)],
)

# Cache em memória para os painéis da navegação (TTL de 60 segundos)
_NAVEGACAO_PAINEIS_CACHE: Dict[int, Dict[str, Any]] = {}
_NAVEGACAO_CACHE_TS: Dict[int, float] = {}
_NAVEGACAO_CACHE_TTL: float = 60.0


def invalidate_navegacao_cache() -> None:
    _NAVEGACAO_PAINEIS_CACHE.clear()
    _NAVEGACAO_CACHE_TS.clear()


DEFAULT_NAVEGACAO_CONFIG: Dict[str, Any] = {
    "janela_meses": 12,
    "grades_epo": [
        {"sigla": "EPO", "nome": "ENFERMAGEM - PRÉ OPERATÓRIO", "ativo": True},
        {"sigla": "EPG", "nome": "ENFERMAGEM PRE-OPERATORIO GINECOLOGIA", "ativo": True},
        {"sigla": "POO", "nome": "ENFERMAGEM PRE-OPERATORIO OTORRINO", "ativo": True},
        {"sigla": "OEP", "nome": "ENFERMAGEM PRE-OPERATORIO PLASTICA", "ativo": True},
        {"sigla": "POT", "nome": "TELEENFERMAGEM PRE-OPERATORIO", "ativo": True},
        {"sigla": "POF", "nome": "ENFERMAGEM PRE-OPERATORIO OFTALMOLOGIA", "ativo": True},
    ],
    "grades_preop": [
        {"sigla": "RIS", "nome": "CARDIO - RISCO CIRURGICO", "ativo": True},
        {"sigla": "PPC", "nome": "PNEUMOLOGIA - PARECER", "ativo": True},
        {"sigla": "RCI", "nome": "CARDIO - RISCO CIRURGICO INFANTIL", "ativo": True},
        {"sigla": "OHR", "nome": "OCI AVALIACAO DE RISCO CIRURGICO", "ativo": True},
        {"sigla": "PPO", "nome": "PNEUMOPEDIATRIA - PRE-OPERATORIO", "ativo": True},
    ],
    "grades_apa": [
        {"sigla": "ANE", "nome": "ANESTESIOLOGIA", "ativo": True},
        {"sigla": "TAN", "nome": "ANESTESIOLOGIA - TELEMEDICINA", "ativo": True},
    ],
    "grupos_exames": [
        {
            "id": "LAB",
            "nome": "Laboratório",
            "ativo": True,
            "incluir_padrao_texto": "",
            "exames": [
                {"sigla": "H", "descricao": "HEMOGRAMA COMPLETO"},
                {"sigla": "G", "descricao": "GLICOSE"},
                {"sigla": "URE", "descricao": "UREIA"},
                {"sigla": "CRE", "descricao": "CREATININA"},
                {"sigla": "TP", "descricao": "TEMPO DE PROTROMBINA"},
                {"sigla": "TTPA", "descricao": "TEMPO DE TROMBOPLASTINA PARCIAL ATIVADA"},
                {"sigla": "COAG", "descricao": "COAGULOGRAMA"},
                {"sigla": "NA", "descricao": "SODIO"},
                {"sigla": "K", "descricao": "POTASSIO"},
                {"sigla": "EAS", "descricao": "SUMARIO DE URINA"},
            ],
        },
        {
            "id": "RAIO_X",
            "nome": "Raio X",
            "ativo": True,
            "incluir_padrao_texto": "",
            "exames": [
                {"sigla": "RXPAP", "descricao": "RX TÓRAX (PA+PERFIL)"},
                {"sigla": "RXCVB", "descricao": "RX CORAÇÃO E VASOS DA BASE - TÓRAX"},
                {"sigla": "RXTX1", "descricao": "TÓRAX ( AP ) LEITO"},
                {"sigla": "RXTX4", "descricao": "TÓRAX (PA+P+OBL)"},
                {"sigla": "RXTX5", "descricao": "TÓRAX ESQUERDO (PA+LAT+OBL)"},
                {"sigla": "RXTX7", "descricao": "TÓRAX (PA-+NSP+EXP+P)"},
                {"sigla": "RXTX9", "descricao": "RX TÓRAX (PARA CONTROLE DE CATÉTER RADIOPACO)"},
                {"sigla": "DL", "descricao": "DIÁLISE LAUDO RX TÓRAX PA + PERFIL"},
            ],
        },
        {
            "id": "ESPIROMETRIA",
            "nome": "Espirometria",
            "ativo": True,
            "incluir_padrao_texto": "",
            "exames": [
                {"sigla": "ESP", "descricao": "ESPIROMETRIA SEM PROVA FARMACODINÂMICA"},
                {"sigla": "ESPB", "descricao": "ESPIROMETRIA COM PROVA FARMACODINÂMICA"},
                {"sigla": "ESPP", "descricao": "ESPIROMETRIA PEDIÁTRICA"},
            ],
        },
        {
            "id": "ECOCARDIOGRAMA",
            "nome": "Ecocardiograma Transtorácico",
            "ativo": True,
            "incluir_padrao_texto": "",
            "exames": [
                {"sigla": "ETT", "descricao": "ECOCARDIOGRAMA TRANSTORÁCICO"},
                {"sigla": "ECO", "descricao": "ECOCARDIOGRAMA"},
                {"sigla": "ECOPE", "descricao": "ECOCARDIOGRAMA PEDIATRICO"},
                {"sigla": "ECOBO", "descricao": "ECOCARDIOGRAMA COM MACROBOLHAS"},
                {"sigla": "ETE", "descricao": "ECOCARDIOGRAMA TRANSESOFÁGICO"},
            ],
        },
        {
            "id": "CINTILOGRAFIA",
            "nome": "Cintilografia Miocárdica",
            "ativo": True,
            "incluir_padrao_texto": "",
            "exames": [
                {"sigla": "CMDIP", "descricao": "CINTILOGRAFIA DO MIOCARDIO COM DIPIRIDAMOL"},
                {"sigla": "CMREP", "descricao": "CINTILOGRAFIA DO MIOCARDIO EM REPOUSO"},
                {"sigla": "CMTLR", "descricao": "CINTILOGRAFIA DO MIOCÁRDIO COM TÁLIO EM REPOUSO"},
                {"sigla": "CMPIR", "descricao": "CINTILOGRAFIA MIOCARCARDICA COM PIROFOSFATO"},
            ],
        },
        {
            "id": "RESSONANCIA",
            "nome": "Ressonância Magnética (Todas)",
            "ativo": True,
            "incluir_padrao_texto": "RESSON",
            "exames": [],
        },
        {
            "id": "HOLTER",
            "nome": "Holter 24h",
            "ativo": True,
            "incluir_padrao_texto": "",
            "exames": [
                {"sigla": "HOLT", "descricao": "HOLTER 24 HORAS"},
            ],
        },
        {
            "id": "TESTE_ESTEIRA",
            "nome": "Teste de Esteira",
            "ativo": True,
            "incluir_padrao_texto": "",
            "exames": [
                {"sigla": "ERGO", "descricao": "ERGOMETRIA (TESTE ERGOMETRICO)"},
                {"sigla": "ERGOE", "descricao": "ERGOESPIROMETRIA"},
            ],
        },
    ],
}


async def _obter_ou_criar_config(db: AsyncSession) -> Dict[str, Any]:
    stmt = select(NavegacaoConfig).where(NavegacaoConfig.id == "default")
    res = await db.execute(stmt)
    obj = res.scalar_one_or_none()
    if obj and obj.config_json:
        try:
            cfg = json.loads(obj.config_json)
            cfg["data_atualizacao"] = obj.data_atualizacao
            cfg["usuario_atualizacao"] = obj.usuario_atualizacao
            return cfg
        except Exception:
            pass

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    novo = NavegacaoConfig(
        id="default",
        config_json=json.dumps(DEFAULT_NAVEGACAO_CONFIG, ensure_ascii=False),
        data_atualizacao=now_str,
        usuario_atualizacao="Sistema",
    )
    db.add(novo)
    await db.commit()
    out = dict(DEFAULT_NAVEGACAO_CONFIG)
    out["data_atualizacao"] = now_str
    out["usuario_atualizacao"] = "Sistema"
    return out


class NavegacaoConfigUpdate(BaseModel):
    janela_meses: int = 12
    grades_epo: List[Dict[str, Any]]
    grades_preop: List[Dict[str, Any]]
    grades_apa: List[Dict[str, Any]]
    grupos_exames: List[Dict[str, Any]]


@router.get("/config", response_model=dict)
async def get_navegacao_config(
    db: AsyncSession = Depends(get_app_db_session),
):
    return await _obter_ou_criar_config(db)


@router.put("/config", response_model=dict)
async def update_navegacao_config(
    payload: NavegacaoConfigUpdate,
    db: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(auth_handler.decode_token),
):
    from .perfil import get_current_user_role
    role = get_current_user_role(user_info)
    groups = user_info.get("groups") or []
    username = str(user_info.get("username") or user_info.get("sub") or "admin").strip()
    if role not in ("ADMIN", "GESTAO_LEC") and "GLO-SEC-HCPE-SETISD" not in groups and username.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas usuários ADMIN ou GESTÃO LEC podem editar a configuração de grades e exames da Navegação.",
        )

    cfg_dict = payload.model_dump()
    cfg_dict["janela_meses"] = max(1, min(60, int(cfg_dict.get("janela_meses") or 12)))
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    stmt = select(NavegacaoConfig).where(NavegacaoConfig.id == "default")
    res = await db.execute(stmt)
    obj = res.scalar_one_or_none()
    if obj:
        obj.config_json = json.dumps(cfg_dict, ensure_ascii=False)
        obj.data_atualizacao = now_str
        obj.usuario_atualizacao = username
    else:
        obj = NavegacaoConfig(
            id="default",
            config_json=json.dumps(cfg_dict, ensure_ascii=False),
            data_atualizacao=now_str,
            usuario_atualizacao=username,
        )
        db.add(obj)
    await db.commit()
    invalidate_navegacao_cache()

    out = dict(cfg_dict)
    out["data_atualizacao"] = now_str
    out["usuario_atualizacao"] = username
    return out


@router.get("/aghu/grades", response_model=List[dict])
async def buscar_grades_aghu(
    q: str = Query("", description="Termo de busca por sigla ou nome da especialidade/grade no AGHU"),
    aghu_db: AsyncSession = Depends(get_aghu_db_session),
):
    """Pesquisa siglas/grades de consulta cadastradas no AGHU para configuração pela Gestão LEC."""
    if not aghu_db:
        return []
    termo = f"%{q.strip().upper()}%" if q and q.strip() else "%"
    sql = text("""
        SELECT
            e.seq AS esp_seq,
            e.sigla AS sigla,
            e.nome_especialidade AS nome,
            e.ind_situacao AS situacao,
            COUNT(g.seq) AS total_grades,
            COUNT(CASE WHEN g.ind_situacao = 'A' THEN 1 END) AS grades_ativas
        FROM agh.agh_especialidades e
        LEFT JOIN agh.aac_grade_agendamen_consultas g ON g.esp_seq = e.seq
        WHERE e.ind_situacao = 'A'
          AND (
            UPPER(e.sigla) LIKE :termo
            OR UPPER(e.nome_especialidade) LIKE :termo
            OR CAST(g.seq AS TEXT) LIKE :termo
          )
        GROUP BY e.seq, e.sigla, e.nome_especialidade, e.ind_situacao
        HAVING COUNT(g.seq) > 0
        ORDER BY e.sigla ASC
        LIMIT 80
    """)
    res = await aghu_db.execute(sql, {"termo": termo})
    return [dict(r) for r in res.mappings().all()]


@router.get("/aghu/exames", response_model=List[dict])
async def buscar_exames_aghu(
    q: str = Query("", description="Termo de busca por sigla ou descrição do exame no AGHU"),
    aghu_db: AsyncSession = Depends(get_aghu_db_session),
):
    """Pesquisa exames ativos no catálogo agh.ael_exames do AGHU para configuração pela Gestão LEC."""
    if not aghu_db:
        return []
    termo = f"%{q.strip().upper()}%" if q and q.strip() else "%"
    sql = text("""
        SELECT
            sigla,
            descricao,
            COALESCE(NULLIF(TRIM(descricao_usual), ''), descricao) AS descricao_usual,
            ind_situacao AS situacao
        FROM agh.ael_exames
        WHERE ind_situacao = 'A'
          AND (
            UPPER(sigla) LIKE :termo
            OR UPPER(descricao) LIKE :termo
            OR UPPER(COALESCE(descricao_usual, '')) LIKE :termo
          )
        ORDER BY descricao ASC
        LIMIT 100
    """)
    res = await aghu_db.execute(sql, {"termo": termo})
    return [dict(r) for r in res.mappings().all()]


def _mapear_status_consulta(
    ret_seq: Optional[int],
    retorno_desc: str,
    dt_consulta: Optional[datetime] = None,
    hoje_date: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Mapeia o ret_seq do AGHU (agh.aac_retornos) e a data da consulta para os status das tabelas da Navegação:
    - Agendado (ret_seq 9 ou 20 com data >= hoje)
    - Agendado (Data Passada) (ret_seq 9 ou 20 com data < hoje, indicando ausência de baixa/desfecho no AGHU)
    - Realizado (ret_seq 10 = PACIENTE ATENDIDO, 60 = EM ATENDIMENTO)
    - Falta do paciente (ret_seq 40 = PACIENTE FALTOU, 50 = PACIENTE DESISTIU CONS)
    - Falta do profissional (ret_seq 30 = PROFISSIONAL FALTOU)
    """
    if hoje_date is None:
        hoje_date = datetime.now().date()
    is_passada = bool(dt_consulta and dt_consulta.date() < hoje_date)

    if ret_seq == 10:
        return {"status": "Realizado", "status_detalhe": "Realizado", "ret_seq": 10, "is_passada": is_passada}
    if ret_seq == 60:
        return {"status": "Realizado", "status_detalhe": "Realizado (Em Atendimento)", "ret_seq": 60, "is_passada": is_passada}
    if ret_seq == 40:
        return {"status": "Falta do paciente", "status_detalhe": "Falta do paciente", "ret_seq": 40, "is_passada": is_passada}
    if ret_seq == 50:
        return {"status": "Falta do paciente", "status_detalhe": "Falta do paciente (Desistiu)", "ret_seq": 50, "is_passada": is_passada}
    if ret_seq == 30:
        return {"status": "Falta do profissional", "status_detalhe": "Falta do profissional", "ret_seq": 30, "is_passada": is_passada}
    if ret_seq in (9, 20) or ret_seq is None:
        if is_passada:
            return {
                "status": "Agendado (Data Passada)",
                "status_detalhe": "Agendado (Data Passada / Sem Desfecho)",
                "ret_seq": ret_seq or 9,
                "is_passada": True,
            }
        det = "Agendado (Aguardando Atendimento)" if ret_seq == 20 else "Agendado"
        return {"status": "Agendado", "status_detalhe": det, "ret_seq": ret_seq or 9, "is_passada": False}

    desc_up = (retorno_desc or "").upper()
    if "ATENDID" in desc_up:
        return {"status": "Realizado", "status_detalhe": retorno_desc or "Realizado", "ret_seq": ret_seq, "is_passada": is_passada}
    if "PROFISSIONAL" in desc_up and "FALT" in desc_up:
        return {"status": "Falta do profissional", "status_detalhe": retorno_desc or "Falta do profissional", "ret_seq": ret_seq, "is_passada": is_passada}
    if "FALT" in desc_up or "DESIST" in desc_up:
        return {"status": "Falta do paciente", "status_detalhe": retorno_desc or "Falta do paciente", "ret_seq": ret_seq, "is_passada": is_passada}
    if is_passada:
        return {
            "status": "Agendado (Data Passada)",
            "status_detalhe": "Agendado (Data Passada / Sem Desfecho)",
            "ret_seq": ret_seq,
            "is_passada": True,
        }
    return {"status": "Agendado", "status_detalhe": retorno_desc or "Agendado", "ret_seq": ret_seq, "is_passada": False}


def _mapear_status_exame(sit_codigo: str, sit_desc: str) -> Dict[str, str]:
    cod = (sit_codigo or "").strip().upper()
    if cod == "LI":
        return {"categoria": "LIBERADO", "label": "Liberado", "cor": "verde"}
    if cod in ("EO", "EX", "AE", "RE", "CO", "CS", "EC"):
        return {"categoria": "EM_ANDAMENTO", "label": sit_desc.title() if sit_desc else "Em Execução", "cor": "azul"}
    if cod in ("AG", "AC", "AX", "PE"):
        return {"categoria": "SOLICITADO", "label": sit_desc.title() if sit_desc else "Solicitado/Agendado", "cor": "amarelo"}
    return {"categoria": "OUTRO", "label": sit_desc.title() if sit_desc else cod, "cor": "cinza"}


@router.get("/paineis", response_model=dict)
async def obter_paineis_navegacao(
    janela_meses: Optional[int] = Query(None, description="Sobrescreve a janela em meses"),
    refresh: bool = Query(False, description="Força recarregamento direto do AGHU ignorando o cache"),
    db: AsyncSession = Depends(get_app_db_session),
    aghu_db: AsyncSession = Depends(get_aghu_db_session),
):
    cfg = await _obter_ou_criar_config(db)
    meses = max(1, min(60, int(janela_meses or cfg.get("janela_meses") or 12)))

    now_mono = time.monotonic()
    if not refresh and meses in _NAVEGACAO_PAINEIS_CACHE and (now_mono - _NAVEGACAO_CACHE_TS.get(meses, 0.0)) < _NAVEGACAO_CACHE_TTL:
        return _NAVEGACAO_PAINEIS_CACHE[meses]

    if not aghu_db:
        vazio = {
            "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "janela_meses": meses,
            "config": cfg,
            "tabela_1_epo_agendada": [],
            "tabela_2_1_epo_faltosa": [],
            "tabela_2_2_epo_realizada": [],
            "tabela_3_1_apa_nao_realizada": [],
            "tabela_3_2_apa_realizada": [],
        }
        return vazio

    siglas_epo = [g["sigla"].strip().upper() for g in cfg.get("grades_epo", []) if g.get("ativo", True) and g.get("sigla")]
    siglas_preop = [g["sigla"].strip().upper() for g in cfg.get("grades_preop", []) if g.get("ativo", True) and g.get("sigla")]
    siglas_apa = [g["sigla"].strip().upper() for g in cfg.get("grades_apa", []) if g.get("ativo", True) and g.get("sigla")]

    set_epo = set(siglas_epo)
    set_apa = set(siglas_apa)
    siglas_principais = list(set_epo | set_apa)

    tabela_1: List[Dict[str, Any]] = []
    tabela_2_1: List[Dict[str, Any]] = []
    tabela_2_2: List[Dict[str, Any]] = []
    tabela_3_1: List[Dict[str, Any]] = []
    tabela_3_2: List[Dict[str, Any]] = []

    if siglas_principais:
        sql_principais = text("""
            SELECT DISTINCT ON (p.prontuario, e.sigla)
                p.prontuario AS prontuario,
                p.codigo AS pac_codigo,
                p.nome AS nome,
                p.nome_social AS nome_social,
                p.dt_nascimento AS dt_nascimento,
                e.sigla AS grade_sigla,
                e.nome_especialidade AS grade_nome,
                c.grd_seq AS grd_seq,
                c.numero AS numero_consulta,
                c.dt_consulta AS dt_consulta,
                c.ret_seq AS ret_seq,
                COALESCE(r.descricao, '') AS retorno_descricao
            FROM agh.aac_consultas c
            JOIN agh.aac_grade_agendamen_consultas g ON c.grd_seq = g.seq
            JOIN agh.agh_especialidades e ON g.esp_seq = e.seq
            JOIN agh.aip_pacientes p ON c.pac_codigo = p.codigo
            LEFT JOIN agh.aac_retornos r ON c.ret_seq = r.seq
            WHERE c.ind_sit_consulta = 'M'
              AND c.pac_codigo IS NOT NULL
              AND p.prontuario IS NOT NULL
              AND e.sigla = ANY(:siglas)
              AND c.dt_consulta >= CURRENT_DATE - (:meses * INTERVAL '1 month')
            ORDER BY p.prontuario, e.sigla, c.dt_consulta DESC
        """)
        res_principais = await aghu_db.execute(sql_principais, {"siglas": siglas_principais, "meses": meses})
        rows_principais = res_principais.mappings().all()

        hoje_date = datetime.now().date()

        # Agrupa as consultas mais recentes por paciente para aplicar a progressão de estágio (Opção A):
        # - Se o paciente já possui APA com data >= data da consulta EPO, ele já avançou para a etapa de APA (Tabelas 3.1 / 3.2) e sai das Tabelas 1 / 2.1 / 2.2.
        # - Se o paciente iniciou novo ciclo com consulta EPO em data > data de uma APA antiga, vale o ciclo atual da EPO (Tabelas 1 / 2.1 / 2.2).
        # - Se o paciente possui múltiplas passagens em diferentes grades dentro do mesmo grupo (ex.: faltou em EPO presencial e depois realizou em POT teleenfermagem), prevalece a passagem mais recente do grupo.
        epo_por_pac: Dict[int, List[Dict[str, Any]]] = {}
        apa_por_pac: Dict[int, List[Dict[str, Any]]] = {}

        for row in rows_principais:
            pac_info = aplicar_nome_social_dict({
                "nome": row["nome"],
                "nome_social": row["nome_social"],
            })
            st = _mapear_status_consulta(row["ret_seq"], row["retorno_descricao"], row["dt_consulta"], hoje_date)
            dt_iso = row["dt_consulta"].strftime("%Y-%m-%d %H:%M") if row["dt_consulta"] else ""
            dt_nasc_iso = row["dt_nascimento"].strftime("%Y-%m-%d") if row["dt_nascimento"] else ""

            item_base = {
                "prontuario": str(row["prontuario"]),
                "pac_codigo": int(row["pac_codigo"]),
                "nome_paciente": pac_info.get("nome") or row["nome"] or "",
                "possui_nome_social": bool(pac_info.get("possui_nome_social")),
                "dt_nascimento": dt_nasc_iso,
                "grade_sigla": row["grade_sigla"],
                "grade_nome": row["grade_nome"],
                "grd_seq": row["grd_seq"],
                "data_consulta": dt_iso,
                "dt_obj": row["dt_consulta"],
                "status": st["status"],
                "status_detalhe": st["status_detalhe"],
                "ret_seq": row["ret_seq"],
            }

            sig = row["grade_sigla"]
            pcod = int(row["pac_codigo"])
            if sig in set_epo:
                epo_por_pac.setdefault(pcod, []).append(item_base)
            if sig in set_apa:
                apa_por_pac.setdefault(pcod, []).append(item_base)

        todos_pacs = set(epo_por_pac.keys()) | set(apa_por_pac.keys())
        for pcod in todos_pacs:
            epos = epo_por_pac.get(pcod, [])
            apas = apa_por_pac.get(pcod, [])

            # Ordena pela data mais recente dentro de cada grupo (EPO e APA)
            epos.sort(key=lambda x: x["data_consulta"] or "", reverse=True)
            apas.sort(key=lambda x: x["data_consulta"] or "", reverse=True)

            epo_atual = epos[0] if epos else None
            apa_atual = apas[0] if apas else None

            dt_epo = epo_atual["dt_obj"] if epo_atual else None
            dt_apa = apa_atual["dt_obj"] if apa_atual else None

            # Progressão de estágio (Opção A):
            # Se existe APA e (não existe EPO ou a APA é posterior/igual ao dia da EPO), o paciente está no estágio de APA (3.1 ou 3.2).
            # Se existe EPO e (não existe APA ou a EPO é posterior ao dia da APA), o paciente está no estágio de EPO (1, 2.1 ou 2.2).
            em_estagio_apa = False
            if apa_atual and not epo_atual:
                em_estagio_apa = True
            elif apa_atual and epo_atual and dt_apa and dt_epo:
                if dt_apa.date() >= dt_epo.date():
                    em_estagio_apa = True

            if em_estagio_apa and apa_atual:
                item_apa = {k: v for k, v in apa_atual.items() if k != "dt_obj"}
                if item_apa["status"] in ("Agendado", "Agendado (Data Passada)", "Falta do paciente", "Falta do profissional"):
                    tabela_3_1.append(item_apa)
                elif item_apa["status"] == "Realizado":
                    tabela_3_2.append(item_apa)
            elif epo_atual:
                item_epo = {k: v for k, v in epo_atual.items() if k != "dt_obj"}
                if item_epo["status"] in ("Agendado", "Agendado (Data Passada)"):
                    tabela_1.append(item_epo)
                elif item_epo["status"] in ("Falta do paciente", "Falta do profissional"):
                    tabela_2_1.append(item_epo)
                elif item_epo["status"] == "Realizado":
                    item_epo["exames_solicitados"] = []
                    item_epo["consultas_preop"] = []
                    tabela_2_2.append(item_epo)

    # Enriquecimento da Tabela 2.2 com Exames Pré-Op e Consultas Pré-Op (RIS, PPC, RCI, OHR, PPO)
    if tabela_2_2:
        pac_codigos_22 = list({item["pac_codigo"] for item in tabela_2_2})
        hoje_date = datetime.now().date()

        # 1) Consultas Pré-Operatórias mais recentes por (pac_codigo, grade_sigla)
        preop_por_pac: Dict[int, List[Dict[str, Any]]] = {}
        if siglas_preop:
            sql_preop = text("""
                SELECT DISTINCT ON (c.pac_codigo, e.sigla)
                    c.pac_codigo AS pac_codigo,
                    e.sigla AS grade_sigla,
                    e.nome_especialidade AS grade_nome,
                    c.grd_seq AS grd_seq,
                    c.dt_consulta AS dt_consulta,
                    c.ret_seq AS ret_seq,
                    COALESCE(r.descricao, '') AS retorno_descricao
                FROM agh.aac_consultas c
                JOIN agh.aac_grade_agendamen_consultas g ON c.grd_seq = g.seq
                JOIN agh.agh_especialidades e ON g.esp_seq = e.seq
                LEFT JOIN agh.aac_retornos r ON c.ret_seq = r.seq
                WHERE c.ind_sit_consulta = 'M'
                  AND c.pac_codigo = ANY(:pac_codigos)
                  AND e.sigla = ANY(:siglas_preop)
                  AND c.dt_consulta >= CURRENT_DATE - (:meses * INTERVAL '1 month')
                ORDER BY c.pac_codigo, e.sigla, c.dt_consulta DESC
            """)
            res_preop = await aghu_db.execute(
                sql_preop,
                {"pac_codigos": pac_codigos_22, "siglas_preop": siglas_preop, "meses": meses},
            )
            for r in res_preop.mappings().all():
                st_p = _mapear_status_consulta(r["ret_seq"], r["retorno_descricao"], r["dt_consulta"], hoje_date)
                dt_p = r["dt_consulta"].strftime("%Y-%m-%d %H:%M") if r["dt_consulta"] else ""
                preop_por_pac.setdefault(int(r["pac_codigo"]), []).append({
                    "sigla": r["grade_sigla"],
                    "nome": r["grade_nome"],
                    "grd_seq": r["grd_seq"],
                    "data": dt_p,
                    "status": st_p["status"],
                    "status_detalhe": st_p["status_detalhe"],
                })

        # 2) Exames Pré-Operatórios solicitados mais recentes por (pac_codigo, exame_sigla)
        sigla_para_grupo: Dict[str, Dict[str, str]] = {}
        padroes_texto_grupos: List[Dict[str, str]] = []

        for grp in cfg.get("grupos_exames", []):
            if not grp.get("ativo", True):
                continue
            g_id = str(grp.get("id") or grp.get("nome") or "").strip()
            g_nome = str(grp.get("nome") or g_id).strip()
            padrao = str(grp.get("incluir_padrao_texto") or "").strip().upper()
            if padrao:
                padroes_texto_grupos.append({"id": g_id, "nome": g_nome, "padrao": padrao})
            for ex in grp.get("exames", []):
                s_ex = str(ex.get("sigla") or "").strip().upper()
                if s_ex:
                    sigla_para_grupo[s_ex] = {"grupo_id": g_id, "grupo_nome": g_nome}

        # Se houver grupos por padrão textual (ex.: RESSONANCIA -> '%RESSON%'), resolve no catálogo ael_exames
        for pt in padroes_texto_grupos:
            sql_pt = text("""
                SELECT sigla
                FROM agh.ael_exames
                WHERE ind_situacao = 'A'
                  AND (UPPER(descricao) LIKE :pat OR UPPER(COALESCE(descricao_usual, '')) LIKE :pat)
            """)
            res_pt = await aghu_db.execute(sql_pt, {"pat": f"%{pt['padrao']}%"})
            for r_pt in res_pt.fetchall():
                s_pt = str(r_pt[0] or "").strip().upper()
                if s_pt and s_pt not in sigla_para_grupo:
                    sigla_para_grupo[s_pt] = {"grupo_id": pt["id"], "grupo_nome": pt["nome"]}

        exames_por_pac: Dict[int, List[Dict[str, Any]]] = {}
        todas_siglas_exames = list(sigla_para_grupo.keys())
        if todas_siglas_exames:
            sql_exames = text("""
                SELECT DISTINCT ON (atd.pac_codigo, ise.ufe_ema_exa_sigla)
                    atd.pac_codigo AS pac_codigo,
                    ise.ufe_ema_exa_sigla AS exame_sigla,
                    COALESCE(NULLIF(TRIM(exa.descricao_usual), ''), exa.descricao) AS exame_nome,
                    ise.sit_codigo AS sit_codigo,
                    COALESCE(sit.descricao, ise.sit_codigo) AS sit_descricao,
                    COALESCE(ise.dthr_programada, soe.criado_em) AS data_exame
                FROM agh.ael_item_solicitacao_exames ise
                JOIN agh.ael_solicitacao_exames soe ON ise.soe_seq = soe.seq
                JOIN agh.agh_atendimentos atd ON soe.atd_seq = atd.seq
                JOIN agh.ael_exames exa ON ise.ufe_ema_exa_sigla = exa.sigla
                LEFT JOIN agh.ael_sit_item_solicitacoes sit ON ise.sit_codigo = sit.codigo
                WHERE atd.pac_codigo = ANY(:pac_codigos)
                  AND ise.ufe_ema_exa_sigla = ANY(:siglas_exames)
                  AND ise.sit_codigo <> 'CA'
                  AND soe.criado_em >= CURRENT_DATE - (:meses * INTERVAL '1 month')
                ORDER BY atd.pac_codigo, ise.ufe_ema_exa_sigla, COALESCE(ise.dthr_programada, soe.criado_em) DESC
            """)
            res_exames = await aghu_db.execute(
                sql_exames,
                {"pac_codigos": pac_codigos_22, "siglas_exames": todas_siglas_exames, "meses": meses},
            )
            for rx in res_exames.mappings().all():
                s_ex = str(rx["exame_sigla"] or "").strip().upper()
                grp_info = sigla_para_grupo.get(s_ex, {"grupo_id": "OUTRO", "grupo_nome": "Outros"})
                st_ex = _mapear_status_exame(rx["sit_codigo"], rx["sit_descricao"])
                dt_ex = rx["data_exame"].strftime("%Y-%m-%d %H:%M") if rx["data_exame"] else ""
                exames_por_pac.setdefault(int(rx["pac_codigo"]), []).append({
                    "sigla": s_ex,
                    "nome": rx["exame_nome"],
                    "grupo_id": grp_info["grupo_id"],
                    "grupo_nome": grp_info["grupo_nome"],
                    "sit_codigo": rx["sit_codigo"],
                    "status": st_ex["label"],
                    "status_categoria": st_ex["categoria"],
                    "cor": st_ex["cor"],
                    "data": dt_ex,
                })

        for item in tabela_2_2:
            pcod = item["pac_codigo"]
            ex_list = exames_por_pac.get(pcod, [])
            ex_list.sort(key=lambda x: (x["grupo_nome"], x["nome"]))
            pre_list = preop_por_pac.get(pcod, [])
            pre_list.sort(key=lambda x: x["sigla"])
            item["exames_solicitados"] = ex_list
            item["consultas_preop"] = pre_list

    # Ordenações especificadas para cada tabela:
    # Tabelas 1, 2.1, 2.2, 3.1: da data mais antiga para a mais recente (ASC)
    # Tabela 3.2: da data mais recente para a mais antiga (DESC)
    tabela_1.sort(key=lambda x: (x["data_consulta"] or "9999-99-99", x["nome_paciente"]))
    tabela_2_1.sort(key=lambda x: (x["data_consulta"] or "9999-99-99", x["nome_paciente"]))
    tabela_2_2.sort(key=lambda x: (x["data_consulta"] or "9999-99-99", x["nome_paciente"]))
    tabela_3_1.sort(key=lambda x: (x["data_consulta"] or "9999-99-99", x["nome_paciente"]))
    tabela_3_2.sort(key=lambda x: (x["data_consulta"] or "", x["nome_paciente"]), reverse=True)

    payload_out = {
        "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "janela_meses": meses,
        "config": cfg,
        "tabela_1_epo_agendada": tabela_1,
        "tabela_2_1_epo_faltosa": tabela_2_1,
        "tabela_2_2_epo_realizada": tabela_2_2,
        "tabela_3_1_apa_nao_realizada": tabela_3_1,
        "tabela_3_2_apa_realizada": tabela_3_2,
    }
    _NAVEGACAO_PAINEIS_CACHE[meses] = payload_out
    _NAVEGACAO_CACHE_TS[meses] = now_mono
    return payload_out
