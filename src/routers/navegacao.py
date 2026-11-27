import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.auth import auth_handler
from ..helpers.historico_helper import registrar_evento_historico
from ..helpers.string_helper import aplicar_nome_social_dict
from ..models.navegacao_config import NavegacaoConfig, NavegacaoClassificacao
from ..models.solicitacao import Solicitacao
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
    "grades_pos_apa": [],
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
            cfg.setdefault("grades_pos_apa", [])
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
    grades_pos_apa: List[Dict[str, Any]] = []
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


CLASSIFICACOES_POR_TABELA: Dict[str, Dict[str, Dict[str, Any]]] = {
    "T1_2": {
        "REAGENDAR_EPO": {
            "label": "Reagendar consulta EPO",
            "requer_acao": True,
            "tipo": "SUBTABELA",
        },
        "SEM_SEGUIMENTO": {
            "label": "Sem seguimento cirúrgico",
            "requer_acao": False,
            "tipo": "SUBTABELA",
        },
        "REALIZADA_SEM_REGISTRO_AGHU": {
            "label": "Realizada (sem registro no AGHU)",
            "requer_acao": False,
            "tipo": "PROMOCAO",
        },
    },
    "T2": {
        "AGENDAR_APA": {
            "label": "Agendar consulta APA",
            "requer_acao": True,
            "tipo": "SUBTABELA",
        },
        "SEM_SEGUIMENTO": {
            "label": "Sem seguimento cirúrgico",
            "requer_acao": False,
            "tipo": "SUBTABELA",
        },
    },
    "T3_2": {
        "REAGENDAR_APA": {
            "label": "Reagendar consulta APA",
            "requer_acao": True,
            "tipo": "SUBTABELA",
        },
        "SEM_SEGUIMENTO": {
            "label": "Sem seguimento cirúrgico",
            "requer_acao": False,
            "tipo": "SUBTABELA",
        },
        "REALIZADA_SEM_REGISTRO_AGHU": {
            "label": "Realizada (sem registro no AGHU)",
            "requer_acao": False,
            "tipo": "PROMOCAO",
        },
    },
    "T4": {
        "PACIENTE_PRONTO_LEC": {
            "label": "Paciente pronto no Sistema LEC",
            "requer_acao": True,
            "tipo": "SUBTABELA",
        },
        "SEM_SEGUIMENTO": {
            "label": "Sem seguimento cirúrgico",
            "requer_acao": False,
            "tipo": "SUBTABELA",
        },
    },
}


def _serializar_classificacao(cls_obj: NavegacaoClassificacao) -> Dict[str, Any]:
    meta = CLASSIFICACOES_POR_TABELA.get(cls_obj.tabela_origem, {}).get(cls_obj.classificacao, {})
    return {
        "id": cls_obj.id,
        "pac_codigo": cls_obj.pac_codigo,
        "prontuario": cls_obj.prontuario,
        "tabela_origem": cls_obj.tabela_origem,
        "numero_consulta_ref": cls_obj.numero_consulta_ref,
        "data_consulta_ref": cls_obj.data_consulta_ref,
        "grade_sigla_ref": cls_obj.grade_sigla_ref,
        "status_consulta_ref": cls_obj.status_consulta_ref,
        "classificacao": cls_obj.classificacao,
        "label": meta.get("label") or cls_obj.classificacao,
        "requer_acao": bool(cls_obj.requer_acao),
        "acao_realizada": bool(cls_obj.acao_realizada),
        "usuario_classificacao": cls_obj.usuario_classificacao,
        "data_classificacao": cls_obj.data_classificacao,
        "usuario_acao": cls_obj.usuario_acao,
        "data_acao": cls_obj.data_acao,
    }


def _classificacao_compativel_com_evento(
    cls_obj: Optional[NavegacaoClassificacao],
    item_evento: Dict[str, Any],
) -> bool:
    """
    Valida o encadeamento temporal entre a classificação registrada e o evento mais recente do AGHU:
    - Se o paciente teve uma nova consulta no AGHU (novo numero_consulta ou nova data_consulta),
      a classificação anterior não se aplica ao novo evento, retornando o paciente para a Lista Principal.
    """
    if not cls_obj:
        return False
    num_ev = item_evento.get("numero_consulta")
    if cls_obj.numero_consulta_ref is not None and num_ev is not None:
        if int(cls_obj.numero_consulta_ref) != int(num_ev):
            return False
    dt_ev = str(item_evento.get("data_consulta") or "").strip()
    dt_ref = str(cls_obj.data_consulta_ref or "").strip()
    if dt_ref and dt_ev and dt_ref != dt_ev:
        return False
    return True


NOMES_TABELAS_NAVEGACAO: Dict[str, str] = {
    "T1_1": "Tabela 1.1 (Consulta EPO agendada)",
    "T1_2": "Tabela 1.2 (Consulta EPO não realizada)",
    "T2": "Tabela 2 (Consulta EPO realizada)",
    "T3_1": "Tabela 3.1 (APA agendada)",
    "T3_2": "Tabela 3.2 (APA não realizada)",
    "T4": "Tabela 4 (APA realizada)",
}


def _obter_perfil_ativo_usuario(user_info: dict) -> str:
    from .perfil import get_current_user_role
    return str(
        user_info.get("perfil_nome")
        or user_info.get("currentProfile")
        or user_info.get("perfil_id")
        or get_current_user_role(user_info)
        or "ADMIN"
    ).strip()


class ClassificarPacientePayload(BaseModel):
    pac_codigo: int
    prontuario: str
    nome_paciente: Optional[str] = "—"
    tabela_origem: str  # 'T1_2', 'T2', 'T3_2', 'T4'
    numero_consulta_ref: Optional[int] = None
    data_consulta_ref: str
    grade_sigla_ref: Optional[str] = None
    grade_nome_ref: Optional[str] = None
    status_consulta_ref: Optional[str] = None
    classificacao: str
    perfil_executor: Optional[str] = None


class TicarAcaoClassificacaoPayload(BaseModel):
    id: str
    acao_realizada: bool = True
    nome_paciente: Optional[str] = None
    perfil_executor: Optional[str] = None


@router.post("/classificar", response_model=dict)
async def classificar_paciente_navegacao(
    payload: ClassificarPacientePayload,
    db: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(auth_handler.decode_token),
):
    tab = (payload.tabela_origem or "").strip().upper()
    cod_cls = (payload.classificacao or "").strip().upper()
    if tab not in CLASSIFICACOES_POR_TABELA or cod_cls not in CLASSIFICACOES_POR_TABELA[tab]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Classificação '{cod_cls}' inválida para a tabela '{tab}'.",
        )

    meta = CLASSIFICACOES_POR_TABELA[tab][cod_cls]
    username = str(user_info.get("username") or user_info.get("sub") or "admin").strip()
    perfil_exec = (payload.perfil_executor or "").strip() or _obter_perfil_ativo_usuario(user_info)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cls_id = f"{int(payload.pac_codigo)}:{tab}"

    stmt = select(NavegacaoClassificacao).where(NavegacaoClassificacao.id == cls_id)
    res = await db.execute(stmt)
    obj = res.scalar_one_or_none()

    if obj:
        obj.prontuario = str(payload.prontuario).strip()
        obj.numero_consulta_ref = payload.numero_consulta_ref
        obj.data_consulta_ref = payload.data_consulta_ref
        obj.grade_sigla_ref = payload.grade_sigla_ref
        obj.status_consulta_ref = payload.status_consulta_ref
        obj.classificacao = cod_cls
        obj.requer_acao = 1 if meta.get("requer_acao") else 0
        obj.acao_realizada = 0
        obj.usuario_classificacao = username
        obj.data_classificacao = now_str
        obj.usuario_acao = None
        obj.data_acao = None
    else:
        obj = NavegacaoClassificacao(
            id=cls_id,
            pac_codigo=int(payload.pac_codigo),
            prontuario=str(payload.prontuario).strip(),
            tabela_origem=tab,
            numero_consulta_ref=payload.numero_consulta_ref,
            data_consulta_ref=payload.data_consulta_ref,
            grade_sigla_ref=payload.grade_sigla_ref,
            status_consulta_ref=payload.status_consulta_ref,
            classificacao=cod_cls,
            requer_acao=1 if meta.get("requer_acao") else 0,
            acao_realizada=0,
            usuario_classificacao=username,
            data_classificacao=now_str,
            usuario_acao=None,
            data_acao=None,
        )
        db.add(obj)

    # Registro no Histórico de Ações (Menu: Navegação)
    # - Se requer_acao == True (ex.: Reagendar consulta EPO, Agendar consulta APA, Reagendar consulta APA, Paciente pronto no Sistema LEC):
    #   Tipo de Evento = SOLICITACAO, Status = PENDENTE
    # - Se requer_acao == False (ex.: Sem seguimento cirúrgico, Realizada (sem registro no AGHU)):
    #   Tipo de Evento = EXECUCAO, Status = CONCLUIDO
    requer_acao_bool = bool(meta.get("requer_acao"))
    tab_nome = NOMES_TABELAS_NAVEGACAO.get(tab, tab)
    grade_info = f"{payload.grade_sigla_ref or '—'}" + (f" ({payload.grade_nome_ref})" if payload.grade_nome_ref else "")
    cod_pront_int = int(payload.prontuario) if str(payload.prontuario).strip().isdigit() else 0
    nome_pac_str = (payload.nome_paciente or "").strip() or f"Paciente #{payload.prontuario}"

    detalhes_hist = (
        f"[Navegação · {tab_nome}] Classificação '{meta['label']}' "
        f"{'registrada com pendência na subtabela' if requer_acao_bool else 'executada diretamente'} "
        f"para o prontuário #{payload.prontuario} ({nome_pac_str}). "
        f"Evento de referência no AGHU: Grade {grade_info} · Data da consulta: {payload.data_consulta_ref or '—'} · "
        f"Status no AGHU: {payload.status_consulta_ref or '—'}."
    )

    await registrar_evento_historico(
        db=db,
        tipo=f"NAV_{cod_cls}",
        origem_menu="Navegação",
        evento_tipo="SOLICITACAO" if requer_acao_bool else "EXECUCAO",
        detalhes=detalhes_hist,
        status="PENDENTE" if requer_acao_bool else "CONCLUIDO",
        especialidade=payload.grade_nome_ref or payload.grade_sigla_ref or "—",
        procedimento=f"{tab_nome} · Consulta {payload.data_consulta_ref or ''}".strip(),
        codigo_paciente=cod_pront_int,
        nome_paciente=nome_pac_str,
        perfil_executor=perfil_exec,
        usuario=username,
    )

    await db.commit()
    invalidate_navegacao_cache()
    return _serializar_classificacao(obj)


@router.post("/classificacao/ticar", response_model=dict)
async def ticar_acao_classificacao_navegacao(
    payload: TicarAcaoClassificacaoPayload,
    db: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(auth_handler.decode_token),
):
    stmt = select(NavegacaoClassificacao).where(NavegacaoClassificacao.id == payload.id)
    res = await db.execute(stmt)
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classificação não encontrada.",
        )

    username = str(user_info.get("username") or user_info.get("sub") or "admin").strip()
    perfil_exec = (payload.perfil_executor or "").strip() or _obter_perfil_ativo_usuario(user_info)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    obj.acao_realizada = 1 if payload.acao_realizada else 0
    obj.usuario_acao = username if payload.acao_realizada else None
    obj.data_acao = now_str if payload.acao_realizada else None

    meta = CLASSIFICACOES_POR_TABELA.get(obj.tabela_origem, {}).get(obj.classificacao, {})
    label_cls = meta.get("label") or obj.classificacao
    tab_nome = NOMES_TABELAS_NAVEGACAO.get(obj.tabela_origem, obj.tabela_origem)
    cod_pront_int = int(obj.prontuario) if str(obj.prontuario).strip().isdigit() else 0
    tipo_hist = f"NAV_{obj.classificacao}"

    # Localiza a solicitação original mais recente desta classificação no histórico para atualizar seu status e vincular a Resposta
    stmt_orig = (
        select(Solicitacao)
        .where(
            Solicitacao.origem_menu == "Navegação",
            Solicitacao.codigo_paciente == cod_pront_int,
            Solicitacao.tipo == tipo_hist,
            Solicitacao.evento_tipo == "SOLICITACAO",
        )
        .order_by(Solicitacao.data_criacao.desc())
    )
    res_orig = await db.execute(stmt_orig)
    solic_orig = res_orig.scalars().first()
    nome_pac_str = (payload.nome_paciente or "").strip() or (solic_orig.nome_paciente if solic_orig else f"Paciente #{obj.prontuario}")
    esp_str = (solic_orig.especialidade if solic_orig else obj.grade_sigla_ref) or "—"
    proc_str = (solic_orig.procedimento if solic_orig else f"{tab_nome} · Consulta {obj.data_consulta_ref or ''}") or "—"

    is_agendamento_consulta = obj.classificacao in ("REAGENDAR_EPO", "AGENDAR_APA", "REAGENDAR_APA")
    termo_cumprimento = "solicitada" if is_agendamento_consulta else "concluída"

    if payload.acao_realizada:
        id_ref_txt = f" #{solic_orig.id}" if solic_orig else ""
        if solic_orig:
            solic_orig.status = "CONCLUIDO"
        detalhes_resp = (
            f"Aprovou a solicitação{id_ref_txt} ({label_cls}). "
            f"Justificativa: Ação '{label_cls}' marcada como {termo_cumprimento} na subtabela da {tab_nome} "
            f"para o prontuário #{obj.prontuario} ({nome_pac_str})."
        )
        await registrar_evento_historico(
            db=db,
            tipo=tipo_hist,
            origem_menu="Navegação",
            evento_tipo="RESPOSTA",
            detalhes=detalhes_resp,
            status="CONCLUIDO",
            especialidade=esp_str,
            procedimento=proc_str,
            codigo_paciente=cod_pront_int,
            nome_paciente=nome_pac_str,
            perfil_executor=perfil_exec,
            usuario=username,
        )
    else:
        if solic_orig:
            solic_orig.status = "PENDENTE"
        detalhes_reab = (
            f"[Navegação · {tab_nome}] Desfez a classificação/marcação de '{label_cls}' como {termo_cumprimento} "
            f"(retornando para Ações Pendentes) para o prontuário #{obj.prontuario} ({nome_pac_str})."
        )
        await registrar_evento_historico(
            db=db,
            tipo=tipo_hist,
            origem_menu="Navegação",
            evento_tipo="CANCELAMENTO_EXECUCAO",
            detalhes=detalhes_reab,
            status="CANCELADO",
            especialidade=esp_str,
            procedimento=proc_str,
            codigo_paciente=cod_pront_int,
            nome_paciente=nome_pac_str,
            perfil_executor=perfil_exec,
            usuario=username,
        )

    await db.commit()
    invalidate_navegacao_cache()
    return _serializar_classificacao(obj)


@router.delete("/classificacao/{classificacao_id:path}", response_model=dict)
async def desfazer_classificacao_navegacao(
    classificacao_id: str,
    perfil_executor: Optional[str] = Query(None),
    nome_paciente: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(auth_handler.decode_token),
):
    stmt = select(NavegacaoClassificacao).where(NavegacaoClassificacao.id == classificacao_id)
    res = await db.execute(stmt)
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classificação não encontrada.",
        )

    username = str(user_info.get("username") or user_info.get("sub") or "admin").strip()
    perfil_exec = (perfil_executor or "").strip() or _obter_perfil_ativo_usuario(user_info)

    pac_cod = obj.pac_codigo
    pront_str = obj.prontuario
    tab_orig = obj.tabela_origem
    cls_tipo = obj.classificacao
    requer_acao_bool = bool(obj.requer_acao)
    acao_ja_realizada_bool = bool(obj.acao_realizada)
    dt_ref = obj.data_consulta_ref
    grade_ref = obj.grade_sigla_ref

    meta = CLASSIFICACOES_POR_TABELA.get(tab_orig, {}).get(cls_tipo, {})
    label_cls = meta.get("label") or cls_tipo
    tab_nome = NOMES_TABELAS_NAVEGACAO.get(tab_orig, tab_orig)
    cod_pront_int = int(pront_str) if str(pront_str).strip().isdigit() else 0
    tipo_hist = f"NAV_{cls_tipo}"

    # Localiza o registro original no histórico
    stmt_orig = (
        select(Solicitacao)
        .where(
            Solicitacao.origem_menu == "Navegação",
            Solicitacao.codigo_paciente == cod_pront_int,
            Solicitacao.tipo == tipo_hist,
        )
        .order_by(Solicitacao.data_criacao.desc())
    )
    res_orig = await db.execute(stmt_orig)
    solic_orig = res_orig.scalars().first()
    nome_pac_str = (nome_paciente or "").strip() or (solic_orig.nome_paciente if solic_orig else f"Paciente #{pront_str}")
    esp_str = (solic_orig.especialidade if solic_orig else grade_ref) or "—"
    proc_str = (solic_orig.procedimento if solic_orig else f"{tab_nome} · Consulta {dt_ref or ''}") or "—"

    # Se era uma ação pendente (check ainda não dado), trata-se de Cancelamento de Solicitação (CANCELAMENTO).
    # Se era uma ação direta ou uma ação já solicitada/check dado que está sendo desfeita, trata-se de Cancelamento (CANCELAMENTO_EXECUCAO).
    is_cancelamento_solicitacao_pendente = requer_acao_bool and not acao_ja_realizada_bool

    if solic_orig and solic_orig.evento_tipo == "SOLICITACAO" and solic_orig.status == "PENDENTE":
        solic_orig.status = "CANCELADO"

    id_ref_txt = f" #{solic_orig.id}" if solic_orig else ""
    await registrar_evento_historico(
        db=db,
        tipo=tipo_hist,
        origem_menu="Navegação",
        evento_tipo="CANCELAMENTO" if is_cancelamento_solicitacao_pendente else "CANCELAMENTO_EXECUCAO",
        detalhes=(
            f"Cancelou a solicitação{id_ref_txt} ({label_cls}): Solicitação pendente '{label_cls}' cancelada na {tab_nome} "
            f"para o prontuário #{pront_str} ({nome_pac_str}), retornando o paciente à Lista Principal."
            if is_cancelamento_solicitacao_pendente
            else f"[Navegação · {tab_nome}] Desfez a classificação '{label_cls}' do prontuário #{pront_str} ({nome_pac_str}), "
            f"retornando o paciente à Lista Principal e status anterior."
        ),
        status="CANCELADO",
        especialidade=esp_str,
        procedimento=proc_str,
        codigo_paciente=cod_pront_int,
        nome_paciente=nome_pac_str,
        perfil_executor=perfil_exec,
        usuario=username,
    )

    await db.delete(obj)

    # Se desfez a promoção REALIZADA_SEM_REGISTRO_AGHU de T1_2 -> T2 ou de T3_2 -> T4,
    # remove também eventual classificação dependente em T2 ou T4 para retornar limpo à lista principal de origem
    if cls_tipo == "REALIZADA_SEM_REGISTRO_AGHU":
        tab_dependente = "T2" if tab_orig == "T1_2" else ("T4" if tab_orig == "T3_2" else None)
        if tab_dependente:
            dep_id = f"{pac_cod}:{tab_dependente}"
            res_dep = await db.execute(select(NavegacaoClassificacao).where(NavegacaoClassificacao.id == dep_id))
            dep_obj = res_dep.scalar_one_or_none()
            if dep_obj:
                await db.delete(dep_obj)

    await db.commit()
    invalidate_navegacao_cache()
    return {"ok": True, "id": classificacao_id}


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
            "tabela_1_1_epo_agendada": [],
            "tabela_1_2_epo_nao_realizada": [],
            "tabela_2_epo_realizada": [],
            "tabela_3_1_apa_agendada": [],
            "tabela_3_2_apa_nao_realizada": [],
            "tabela_4_apa_realizada": [],
        }
        return vazio

    siglas_epo = [g["sigla"].strip().upper() for g in cfg.get("grades_epo", []) if g.get("ativo", True) and g.get("sigla")]
    siglas_preop = [g["sigla"].strip().upper() for g in cfg.get("grades_preop", []) if g.get("ativo", True) and g.get("sigla")]
    siglas_apa = [g["sigla"].strip().upper() for g in cfg.get("grades_apa", []) if g.get("ativo", True) and g.get("sigla")]
    siglas_pos_apa = [g["sigla"].strip().upper() for g in cfg.get("grades_pos_apa", []) if g.get("ativo", True) and g.get("sigla")]

    set_epo = set(siglas_epo)
    set_apa = set(siglas_apa)
    siglas_principais = list(set_epo | set_apa)

    # Carrega todas as classificações persistidas no SQLite para cruzamento por (pac_codigo, tabela_origem)
    res_cls_all = await db.execute(select(NavegacaoClassificacao))
    classif_por_pac_tab: Dict[Any, NavegacaoClassificacao] = {
        (int(c.pac_codigo), str(c.tabela_origem)): c for c in res_cls_all.scalars().all()
    }

    tabela_1_1: List[Dict[str, Any]] = []
    tabela_1_2: List[Dict[str, Any]] = []
    tabela_2: List[Dict[str, Any]] = []
    tabela_3_1: List[Dict[str, Any]] = []
    tabela_3_2: List[Dict[str, Any]] = []
    tabela_4: List[Dict[str, Any]] = []

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
                "numero_consulta": int(row["numero_consulta"]) if row["numero_consulta"] is not None else None,
                "data_consulta": dt_iso,
                "dt_obj": row["dt_consulta"],
                "status": st["status"],
                "status_detalhe": st["status_detalhe"],
                "status_original_aghu": st["status"],
                "status_detalhe_original_aghu": st["status_detalhe"],
                "ret_seq": row["ret_seq"],
                "subtabela": "PRINCIPAL",
                "classificacao_info": None,
                "promovido_sem_registro": False,
                "promocao_info": None,
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
            # Se existe APA e (não existe EPO ou a APA é posterior/igual ao dia da EPO), o paciente está no estágio de APA (3.1, 3.2 ou 4).
            # Se existe EPO e (não existe APA ou a EPO é posterior ao dia da APA), o paciente está no estágio de EPO (1.1, 1.2 ou 2).
            em_estagio_apa = False
            if apa_atual and not epo_atual:
                em_estagio_apa = True
            elif apa_atual and epo_atual and dt_apa and dt_epo:
                if dt_apa.date() >= dt_epo.date():
                    em_estagio_apa = True

            if em_estagio_apa and apa_atual:
                item_apa = {k: v for k, v in apa_atual.items() if k != "dt_obj"}
                if item_apa["status"] == "Agendado":
                    tabela_3_1.append(item_apa)
                elif item_apa["status"] in ("Agendado (Data Passada)", "Falta do paciente", "Falta do profissional"):
                    cls_32 = classif_por_pac_tab.get((pcod, "T3_2"))
                    if _classificacao_compativel_com_evento(cls_32, item_apa):
                        if cls_32.classificacao == "REALIZADA_SEM_REGISTRO_AGHU":
                            item_apa["status"] = "Realizado"
                            item_apa["status_detalhe"] = "Realizado (sem registro no AGHU)"
                            item_apa["promovido_sem_registro"] = True
                            item_apa["promocao_info"] = _serializar_classificacao(cls_32)
                            item_apa["consultas_pos_apa"] = []
                            cls_4 = classif_por_pac_tab.get((pcod, "T4"))
                            if _classificacao_compativel_com_evento(cls_4, item_apa):
                                item_apa["subtabela"] = cls_4.classificacao
                                item_apa["classificacao_info"] = _serializar_classificacao(cls_4)
                            tabela_4.append(item_apa)
                        else:
                            item_apa["subtabela"] = cls_32.classificacao
                            item_apa["classificacao_info"] = _serializar_classificacao(cls_32)
                            tabela_3_2.append(item_apa)
                    else:
                        tabela_3_2.append(item_apa)
                elif item_apa["status"] == "Realizado":
                    item_apa["consultas_pos_apa"] = []
                    cls_4 = classif_por_pac_tab.get((pcod, "T4"))
                    if _classificacao_compativel_com_evento(cls_4, item_apa):
                        item_apa["subtabela"] = cls_4.classificacao
                        item_apa["classificacao_info"] = _serializar_classificacao(cls_4)
                    tabela_4.append(item_apa)
            elif epo_atual:
                item_epo = {k: v for k, v in epo_atual.items() if k != "dt_obj"}
                if item_epo["status"] == "Agendado":
                    tabela_1_1.append(item_epo)
                elif item_epo["status"] in ("Agendado (Data Passada)", "Falta do paciente", "Falta do profissional"):
                    cls_12 = classif_por_pac_tab.get((pcod, "T1_2"))
                    if _classificacao_compativel_com_evento(cls_12, item_epo):
                        if cls_12.classificacao == "REALIZADA_SEM_REGISTRO_AGHU":
                            item_epo["status"] = "Realizado"
                            item_epo["status_detalhe"] = "Realizado (sem registro no AGHU)"
                            item_epo["promovido_sem_registro"] = True
                            item_epo["promocao_info"] = _serializar_classificacao(cls_12)
                            item_epo["exames_solicitados"] = []
                            item_epo["consultas_preop"] = []
                            cls_2 = classif_por_pac_tab.get((pcod, "T2"))
                            if _classificacao_compativel_com_evento(cls_2, item_epo):
                                item_epo["subtabela"] = cls_2.classificacao
                                item_epo["classificacao_info"] = _serializar_classificacao(cls_2)
                            tabela_2.append(item_epo)
                        else:
                            item_epo["subtabela"] = cls_12.classificacao
                            item_epo["classificacao_info"] = _serializar_classificacao(cls_12)
                            tabela_1_2.append(item_epo)
                    else:
                        tabela_1_2.append(item_epo)
                elif item_epo["status"] == "Realizado":
                    item_epo["exames_solicitados"] = []
                    item_epo["consultas_preop"] = []
                    cls_2 = classif_por_pac_tab.get((pcod, "T2"))
                    if _classificacao_compativel_com_evento(cls_2, item_epo):
                        item_epo["subtabela"] = cls_2.classificacao
                        item_epo["classificacao_info"] = _serializar_classificacao(cls_2)
                    tabela_2.append(item_epo)

    # Enriquecimento da Tabela 2 (Consulta EPO realizada) com Exames Pré-Op e Consultas Pré-Op (RIS, PPC, RCI, OHR, PPO)
    if tabela_2:
        pac_codigos_2 = list({item["pac_codigo"] for item in tabela_2})
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
                {"pac_codigos": pac_codigos_2, "siglas_preop": siglas_preop, "meses": meses},
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
                {"pac_codigos": pac_codigos_2, "siglas_exames": todas_siglas_exames, "meses": meses},
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

        for item in tabela_2:
            pcod = item["pac_codigo"]
            ex_list = exames_por_pac.get(pcod, [])
            ex_list.sort(key=lambda x: (x["grupo_nome"], x["nome"]))
            pre_list = preop_por_pac.get(pcod, [])
            pre_list.sort(key=lambda x: x["sigla"])
            item["exames_solicitados"] = ex_list
            item["consultas_preop"] = pre_list

    # Enriquecimento da Tabela 4 (APA realizada) com Consultas Solicitadas pela APA (grades_pos_apa)
    if tabela_4:
        pac_codigos_4 = list({item["pac_codigo"] for item in tabela_4})
        hoje_date = datetime.now().date()
        pos_apa_por_pac: Dict[int, List[Dict[str, Any]]] = {}

        if siglas_pos_apa:
            sql_pos_apa = text("""
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
                  AND e.sigla = ANY(:siglas_pos_apa)
                  AND c.dt_consulta >= CURRENT_DATE - (:meses * INTERVAL '1 month')
                ORDER BY c.pac_codigo, e.sigla, c.dt_consulta DESC
            """)
            res_pos_apa = await aghu_db.execute(
                sql_pos_apa,
                {"pac_codigos": pac_codigos_4, "siglas_pos_apa": siglas_pos_apa, "meses": meses},
            )
            for r in res_pos_apa.mappings().all():
                st_pa = _mapear_status_consulta(r["ret_seq"], r["retorno_descricao"], r["dt_consulta"], hoje_date)
                dt_pa = r["dt_consulta"].strftime("%Y-%m-%d %H:%M") if r["dt_consulta"] else ""
                pos_apa_por_pac.setdefault(int(r["pac_codigo"]), []).append({
                    "sigla": r["grade_sigla"],
                    "nome": r["grade_nome"],
                    "grd_seq": r["grd_seq"],
                    "data": dt_pa,
                    "status": st_pa["status"],
                    "status_detalhe": st_pa["status_detalhe"],
                })

        for item in tabela_4:
            pcod = item["pac_codigo"]
            pa_list = pos_apa_por_pac.get(pcod, [])
            pa_list.sort(key=lambda x: x["sigla"])
            item["consultas_pos_apa"] = pa_list

    # Ordenações especificadas para cada tabela:
    # Todas as 6 tabelas (1.1, 1.2, 2, 3.1, 3.2 e 4): da data mais antiga para a mais recente (ASC)
    tabela_1_1.sort(key=lambda x: (x["data_consulta"] or "9999-99-99", x["nome_paciente"]))
    tabela_1_2.sort(key=lambda x: (x["data_consulta"] or "9999-99-99", x["nome_paciente"]))
    tabela_2.sort(key=lambda x: (x["data_consulta"] or "9999-99-99", x["nome_paciente"]))
    tabela_3_1.sort(key=lambda x: (x["data_consulta"] or "9999-99-99", x["nome_paciente"]))
    tabela_3_2.sort(key=lambda x: (x["data_consulta"] or "9999-99-99", x["nome_paciente"]))
    tabela_4.sort(key=lambda x: (x["data_consulta"] or "9999-99-99", x["nome_paciente"]))

    payload_out = {
        "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "janela_meses": meses,
        "config": cfg,
        "tabela_1_1_epo_agendada": tabela_1_1,
        "tabela_1_2_epo_nao_realizada": tabela_1_2,
        "tabela_2_epo_realizada": tabela_2,
        "tabela_3_1_apa_agendada": tabela_3_1,
        "tabela_3_2_apa_nao_realizada": tabela_3_2,
        "tabela_4_apa_realizada": tabela_4,
    }
    _NAVEGACAO_PAINEIS_CACHE[meses] = payload_out
    _NAVEGACAO_CACHE_TS[meses] = now_mono
    return payload_out
