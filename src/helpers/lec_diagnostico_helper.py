# src/helpers/lec_diagnostico_helper.py

import io
import json
import re
import uuid
import zipfile
import unicodedata
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, desc

from ..models.user import User
from ..models.profile import Profile
from ..models.paciente import Paciente
from ..models.solicitacao import Solicitacao
from ..models.diagnostico_lec import DiagnosticoLec
from ..helpers.string_helper import (
    generate_profile_id,
    remove_accents,
    normalize_specialty_name,
    resolver_nome_paciente,
)


LEC_TO_CANONICAL_KEY: Dict[str, str] = {
    "CIRURGIA BARIATRICA": "BARIATRICA",
    "BARIATRICA": "BARIATRICA",
    "ODONTOLOGIA - CIRURGIA BUCOMAXILOFACIAL": "BUCOMAXILOFACIAL",
    "CIRURGIA BUCOMAXILOFACIAL": "BUCOMAXILOFACIAL",
    "BUCOMAXILOFACIAL": "BUCOMAXILOFACIAL",
    "CIRURGIA DE CABECA E PESCOCO": "CABECA E PESCOCO",
    "CABECA E PESCOCO": "CABECA E PESCOCO",
    "CARDIOLOGIA - CIRURGIA CARDIACA": "CARDIACA",
    "CIRURGIA CARDIACA": "CARDIACA",
    "CARDIACA": "CARDIACA",
    "DERMATOLOGIA": "DERMATOLOGIA",
    "MASTOLOGIA - ESPACO TRANS": "ESPACO TRANS",
    "ESPACO TRANS": "ESPACO TRANS",
    "CIRURGIA GERAL": "GERAL",
    "CIRURGIA_GERAL": "GERAL",
    "CIRURGIA DO APARELHO DIGESTIVO": "GERAL",
    "APARELHO DIGESTIVO": "GERAL",
    "APARELHO_DIGESTIVO": "GERAL",
    "PROCTOLOGIA": "GERAL",
    "GERAL": "GERAL",
    "GINECOLOGIA - HISTEROSCOPIA CIRURGICA": "GINECOLOGIA ENDOSCOPICA",
    "GINECOLOGIA ENDOSCOPICA": "GINECOLOGIA ENDOSCOPICA",
    "GINECOLOGIA": "GINECOLOGIA GERAL",
    "GINECOLOGIA GERAL": "GINECOLOGIA GERAL",
    "HEMODINAMICA": "HEMODINAMICA",
    "NEUROCIRURGIA": "NEUROCIRURGIA",
    "OFTALMOLOGIA": "OFTALMOLOGIA",
    "CIRURGIA ONCOLOGICA": "ONCOLOGICA",
    "ONCOLOGICA": "ONCOLOGICA",
    "ORTOPEDIA E TRAUMATOLOGIA": "ORTOPEDIA",
    "ORTOPEDIA": "ORTOPEDIA",
    "OTORRINOLARINGOLOGIA": "OTORRINOLARINGOLOGIA",
    "CIRURGIA PEDIATRICA": "PEDIATRICA",
    "PEDIATRICA": "PEDIATRICA",
    "CIRURGIA PLASTICA": "PLASTICA",
    "PLASTICA": "PLASTICA",
    "CIRURGIA TORACICA": "TORACICA",
    "TORACICA": "TORACICA",
    "UROLOGIA": "UROLOGIA",
}

CANONICAL_DISPLAY_NAME: Dict[str, str] = {
    "BARIATRICA": "BARIÁTRICA",
    "BUCOMAXILOFACIAL": "BUCOMAXILOFACIAL",
    "CABECA E PESCOCO": "CABEÇA E PESCOÇO",
    "CARDIACA": "CARDÍACA",
    "DERMATOLOGIA": "DERMATOLOGIA",
    "ESPACO TRANS": "ESPAÇO TRANS",
    "GERAL": "GERAL",
    "GINECOLOGIA ENDOSCOPICA": "GINECOLOGIA ENDOSCÓPICA",
    "GINECOLOGIA GERAL": "GINECOLOGIA GERAL",
    "HEMODINAMICA": "HEMODINÂMICA",
    "NEUROCIRURGIA": "NEUROCIRURGIA",
    "OFTALMOLOGIA": "OFTALMOLOGIA",
    "ONCOLOGICA": "ONCOLÓGICA",
    "ORTOPEDIA": "ORTOPEDIA",
    "OTORRINOLARINGOLOGIA": "OTORRINOLARINGOLOGIA",
    "PEDIATRICA": "PEDIÁTRICA",
    "PLASTICA": "PLÁSTICA",
    "TORACICA": "TORÁCICA",
    "UROLOGIA": "UROLOGIA",
}


def strip_accents_upper(val: Optional[str]) -> str:
    if not val:
        return ""
    s = unicodedata.normalize("NFD", str(val))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return " ".join(s.upper().strip().split())


def normalize_lec_specialty_key(raw_esp: Optional[str]) -> str:
    """Retorna a chave canônica sem acentos (ex: 'BARIATRICA', 'GERAL')."""
    e = strip_accents_upper(raw_esp)
    if not e:
        return ""
    if e in LEC_TO_CANONICAL_KEY:
        return LEC_TO_CANONICAL_KEY[e]
    if e in (
        "CIRURGIA GERAL",
        "CIRURGIA_GERAL",
        "APARELHO DIGESTIVO",
        "APARELHO_DIGESTIVO",
        "CIRURGIA DO APARELHO DIGESTIVO",
        "PROCTOLOGIA",
        "GERAL",
    ):
        return "GERAL"
    if "CARDIACA" in e:
        return "CARDIACA"
    if "BARIATRICA" in e:
        return "BARIATRICA"
    if "CABECA" in e:
        return "CABECA E PESCOCO"
    if "ONCOLOGICA" in e:
        return "ONCOLOGICA"
    if "PEDIATRICA" in e:
        return "PEDIATRICA"
    if "PLASTICA" in e:
        return "PLASTICA"
    if "TORACICA" in e:
        return "TORACICA"
    if "DERMATOLOGIA" in e:
        return "DERMATOLOGIA"
    if "HISTEROSCOPIA" in e or "ENDOSCOPICA" in e:
        return "GINECOLOGIA ENDOSCOPICA"
    if "GINECOLOGIA" in e:
        return "GINECOLOGIA GERAL"
    if "HEMODINAMICA" in e:
        return "HEMODINAMICA"
    if "MASTO" in e or "ESPACO TRANS" in e:
        return "ESPACO TRANS"
    if "NEURO" in e:
        return "NEUROCIRURGIA"
    if "OFTALMO" in e:
        return "OFTALMOLOGIA"
    if "ORTOPEDIA" in e:
        return "ORTOPEDIA"
    if "OTORRINO" in e:
        return "OTORRINOLARINGOLOGIA"
    if "UROLOGIA" in e:
        return "UROLOGIA"
    if "BUCO" in e:
        return "BUCOMAXILOFACIAL"
    norm = strip_accents_upper(normalize_specialty_name(e))
    return LEC_TO_CANONICAL_KEY.get(norm, norm)


def get_display_specialty(esp_key_or_raw: Optional[str]) -> str:
    """Retorna o nome de exibição oficial com acentos (ex: 'BARIÁTRICA')."""
    key = normalize_lec_specialty_key(esp_key_or_raw)
    return CANONICAL_DISPLAY_NAME.get(key, key or "NÃO INFORMADA")


def clean_proc_base(proc_str: Optional[str]) -> str:
    if not proc_str:
        return ""
    p = strip_accents_upper(proc_str)
    p = re.sub(r"\s*\((?:ID\s*)?\d+\)\s*$", "", p)
    return " ".join(p.split())


def normalize_lateralidade(val: Optional[str]) -> str:
    if not val:
        return "Indefinida"
    s = strip_accents_upper(val)
    if not s or s in ("NONE", "NULL", "—", "-", "NAO SE APLICA", "INDEFINIDA", "INDEFINIDO", "NAO INFORMADO"):
        return "Indefinida"
    if "BILATERAL" in s:
        return "Bilateral"
    if "DIREIT" in s:
        return "Direita"
    if "ESQUERD" in s:
        return "Esquerda"
    return val.strip().title()


def normalize_swalis(val: Optional[str]) -> str:
    if not val:
        return "—"
    s = strip_accents_upper(val)
    if s in ("NONE", "NULL", "—", "-", ""):
        return "—"
    return s


def normalize_judicializado(val: Optional[str]) -> str:
    if not val:
        return "Não"
    s = strip_accents_upper(val)
    if s in ("S", "SIM", "1", "TRUE", "V", "VERDADEIRO"):
        return "Sim"
    return "Não"


def clean_cell(val: Any) -> str:
    if pd.isna(val) or val is None:
        return ""
    if hasattr(val, "strftime"):
        try:
            return val.strftime("%Y-%m-%d %H:%M")
        except Exception:
            pass
    s = str(val).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s


def _extract_excel_files(uploaded_files: List[Tuple[str, bytes]]) -> List[Tuple[str, bytes]]:
    """Extrai arquivos .xlsx/.xls de uploads diretos ou de dentro de arquivos .zip."""
    extracted: List[Tuple[str, bytes]] = []
    for fname, fbytes in uploaded_files:
        lower_name = (fname or "").lower()
        if lower_name.endswith(".zip"):
            try:
                with zipfile.ZipFile(io.BytesIO(fbytes)) as zf:
                    for info in sorted(zf.infolist(), key=lambda x: x.filename):
                        base_name = info.filename.split("/")[-1].split("\\")[-1]
                        if (
                            not info.is_dir()
                            and not base_name.startswith("~$")
                            and not base_name.startswith(".")
                            and "__macosx" not in info.filename.lower()
                            and base_name.lower().endswith((".xlsx", ".xls"))
                        ):
                            extracted.append((base_name, zf.read(info.filename)))
            except Exception as e:
                raise ValueError(f"Não foi possível descompactar o arquivo ZIP '{fname}': {e}")
        elif lower_name.endswith((".xlsx", ".xls")):
            extracted.append((fname, fbytes))
    return extracted


def _parse_single_lec_excel(filename: str, file_bytes: bytes) -> Dict[str, Any]:
    """
    Lê uma planilha exportada do Sistema LEC e retorna os registros estruturados.
    Utiliza openpyxl em modo read_only para altíssima performance em lotes ZIP.
    """
    import warnings
    import openpyxl

    rows_iter: List[Tuple[Any, ...]] = []
    headers: List[str] = []

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wb = openpyxl.load_workbook(io.BytesIO(file_bytes), read_only=True, data_only=True)
            ws = wb.active
            all_rows = list(ws.iter_rows(values_only=True))
            wb.close()
            if all_rows:
                headers = [str(c or "") for c in all_rows[0]]
                rows_iter = all_rows[1:]
    except Exception:
        stream = io.BytesIO(file_bytes)
        df = None
        last_err = None
        for engine in ["openpyxl", "xlrd", None]:
            try:
                stream.seek(0)
                df = pd.read_excel(stream, header=0, engine=engine) if engine else pd.read_excel(stream, header=0)
                break
            except Exception as err:
                last_err = err
        if df is None:
            raise ValueError(f"Erro ao ler a planilha '{filename}': {last_err}")
        headers = [str(c or "") for c in df.columns]
        rows_iter = [tuple(r) for r in df.itertuples(index=False, name=None)]

    col_map: Dict[str, int] = {}
    for idx, col in enumerate(headers):
        norm_c = strip_accents_upper(str(col)).replace(" ", "_")
        if norm_c:
            col_map[norm_c] = idx

    def get_val(row_vals: tuple, candidates: List[str], fallback_idx: Optional[int] = None) -> str:
        for c in candidates:
            if c in col_map and col_map[c] < len(row_vals):
                return clean_cell(row_vals[col_map[c]])
        if fallback_idx is not None and fallback_idx < len(row_vals):
            return clean_cell(row_vals[fallback_idx])
        return ""

    records: List[Dict[str, Any]] = []
    raw_specialties_seen = set()

    for vals in rows_iter:
        if not vals or len(vals) < 2:
            continue

        raw_pront = get_val(vals, ["PRONTUARIO", "COD_PRONTUARIO", "PRONT"], 1)
        if not raw_pront or not raw_pront.isdigit():
            continue
        pront_int = int(raw_pront)

        raw_pac = get_val(vals, ["NOME_DO_PACIENTE", "PACIENTE", "NOME_PACIENTE", "NOME"], None)
        raw_esp = get_val(vals, ["ESPECIALIDADE", "NOME_ESPECIALIDADE", "LISTA_DE_ESPERA", "LISTA", "ID_ESPECIALIDADE"], None)
        raw_proc = get_val(vals, ["PROCEDIMENTO", "NOME_PROCEDIMENTO", "ID_PROCEDIMENTO"], None)
        raw_dth = get_val(vals, ["DATA_DE_INDICACAO", "DTH_INDICACAO", "DATA_DE_INCLUSAO", "DATA_INDICACAO", "DTH_INDICACAO_FILA"], None)
        raw_swalis = get_val(vals, ["SWALIS", "PRIORIDADE_SWALIS", "SWALLIS"], None)
        raw_medico = get_val(vals, ["MEDICO_RESPONSAVEL", "MEDICO", "CRM"], None)
        raw_jud = get_val(vals, ["JUDICIALIZADO", "SIN_JUDICIALIZADO"], None)
        raw_lat = get_val(vals, ["LATERALIDADE", "LADO"], None)
        raw_motivo = get_val(vals, ["SITUACAO", "STATUS", "MOTIVO_STATUS", "ID_MOTIVO_STATUS"], None)

        raw_esp_clean = strip_accents_upper(raw_esp) or "NAO_IDENTIFICADA"
        raw_specialties_seen.add(raw_esp_clean)
        esp_key = normalize_lec_specialty_key(raw_esp_clean)

        jud_str = normalize_judicializado(raw_jud)
        swalis_str = normalize_swalis(raw_swalis)
        lat_str = normalize_lateralidade(raw_lat)
        medico_str = (raw_medico or "").strip().upper() or "Não informado"

        dth_fmt = raw_dth
        if re.match(r"^\d{2}/\d{2}/\d{4}", raw_dth):
            parts = raw_dth.split(" ")
            d_parts = parts[0].split("/")
            hora = parts[1][:5] if len(parts) > 1 else "00:00"
            dth_fmt = f"{d_parts[2]}-{d_parts[1]}-{d_parts[0]} {hora}"
        elif re.match(r"^\d{4}-\d{2}-\d{2}", raw_dth):
            dth_fmt = raw_dth[:16]

        records.append({
            "prontuario": pront_int,
            "nome_paciente": raw_pac or f"PACIENTE {pront_int}",
            "raw_especialidade": raw_esp_clean,
            "esp_key": esp_key,
            "especialidade_display": get_display_specialty(esp_key),
            "procedimento": raw_proc or "PROCEDIMENTO NÃO ESPECIFICADO",
            "proc_base": clean_proc_base(raw_proc),
            "data_indicacao": dth_fmt or datetime.now().strftime("%Y-%m-%d %H:%M"),
            "data_indicacao_original": raw_dth or "—",
            "swalis": swalis_str,
            "medico_responsavel": medico_str,
            "lateralidade": lat_str,
            "judicializado": jud_str,
            "motivo_status": raw_motivo or "Ativo",
            "arquivo_origem": filename,
        })

    primary_raw_esp = next(iter(raw_specialties_seen)) if raw_specialties_seen else "VAZIO"
    primary_esp_key = normalize_lec_specialty_key(primary_raw_esp)
    pronts_set = {r["prontuario"] for r in records}

    return {
        "filename": filename,
        "raw_esp": primary_raw_esp,
        "esp_key": primary_esp_key,
        "especialidade_display": get_display_specialty(primary_esp_key),
        "records": records,
        "pronts_set": pronts_set,
        "total_linhas": len(records),
    }


async def _reconstruct_cc_state(app_db: AsyncSession) -> Dict[str, Any]:
    """
    Reconstrói em memória o estado exato da fila ativa do Comunicação Cirúrgica
    (idêntico a Pacientes.vue), resolvendo também o nome completo do médico responsável
    a partir da tabela `usuarios`.
    """
    # 1. Mapa de login -> Nome Completo dos médicos/profissionais
    res_users = await app_db.execute(select(User))
    user_login_to_name: Dict[str, str] = {}
    for u in res_users.scalars().all():
        if u.username and u.nome:
            user_login_to_name[u.username.strip().lower()] = u.nome.strip().upper()
            user_login_to_name[u.nome.strip().lower()] = u.nome.strip().upper()

    def resolve_medico_cc(raw_med: Optional[str]) -> str:
        if not raw_med or raw_med.strip() in ("", "—", "Não informado", "NAO_INFORMADO"):
            return "Não informado"
        clean = raw_med.strip()
        return user_login_to_name.get(clean.lower(), clean.upper())

    # 2. Pacientes locais
    res_pac = await app_db.execute(select(Paciente))
    pac_rows = res_pac.scalars().all()
    pac_name_map: Dict[int, str] = {}
    pac_table_by_pront: Dict[int, List[Paciente]] = {}
    for p in pac_rows:
        if p.codigo is None:
            continue
        nome_exibicao = resolver_nome_paciente(p.nome, getattr(p, "nome_social", None))
        pac_name_map[p.codigo] = nome_exibicao
        pac_table_by_pront.setdefault(p.codigo, []).append(p)

    # 3. Solicitações (ignorando eventos de log 'RESPOSTA', 'ALTERACAO', 'EDICAO', 'CANCELAMENTO')
    res_sol = await app_db.execute(select(Solicitacao).order_by(Solicitacao.data_criacao.asc(), Solicitacao.id.asc()))
    sol_rows = res_sol.scalars().all()

    active_by_pront: Dict[int, List[Dict[str, Any]]] = {}
    excluded_by_esp_pront: Dict[Tuple[str, int], Dict[str, Any]] = {}
    pending_by_esp_pront: Dict[Tuple[str, int], Dict[str, Any]] = {}

    for s in sol_rows:
        if not s.codigo_paciente or s.codigo_paciente == 0:
            continue
        proc_str = s.procedimento or ""
        if proc_str.lower().startswith("perfil:") or (s.origem_menu or "").lower() == "perfis":
            continue

        ev_tipo = (s.evento_tipo or "").upper()
        pront = int(s.codigo_paciente)
        esp_key = normalize_lec_specialty_key(s.especialidade)
        if not esp_key or esp_key == "TESTE":
            continue

        if s.nome_paciente and (pront not in pac_name_map or str(pac_name_map[pront]).startswith("PACIENTE ")):
            pac_name_map[pront] = s.nome_paciente

        if s.status == "PENDENTE":
            if ev_tipo not in ("RESPOSTA", "ALTERACAO", "EDICAO", "CANCELAMENTO"):
                pending_by_esp_pront[(esp_key, pront)] = {
                    "id": s.id,
                    "tipo": s.tipo,
                    "procedimento": proc_str,
                    "data_criacao": s.data_criacao or "—",
                    "usuario": s.usuario or s.medico_responsavel or "—",
                }
            continue

        if s.status != "APROVADO" or ev_tipo in ("RESPOSTA", "ALTERACAO", "CANCELAMENTO"):
            continue

        proc_b = clean_proc_base(proc_str)

        if s.tipo == "INSERIR":
            plist = active_by_pront.setdefault(pront, [])
            plist.append({
                "sol_id": s.id,
                "esp_key": esp_key,
                "especialidade_display": get_display_specialty(esp_key),
                "procedimento": proc_str,
                "proc_base": proc_b,
                "data_criacao": s.data_criacao or "—",
                "medico_responsavel": resolve_medico_cc(s.medico_responsavel),
                "medico_raw": s.medico_responsavel or "",
                "swalis": normalize_swalis(s.swallis),
                "lateralidade": normalize_lateralidade(getattr(s, "lateralidade", None)),
                "judicializado": normalize_judicializado(s.judicializado),
                "detalhes": s.detalhes or "",
                "usuario": s.usuario or "Sistema",
                "is_importacao_fila": str(s.id or "").startswith("SOL-FILA-") or "Importação de fila" in (s.detalhes or ""),
            })
        elif s.tipo == "EDITAR":
            plist = active_by_pront.get(pront, [])
            target_proc = s.procedimento_anterior or proc_str
            found = next(
                (
                    x
                    for x in plist
                    if (s.id and x["sol_id"] == s.id)
                    or (x["esp_key"] == esp_key and x["procedimento"] == target_proc)
                    or (x["esp_key"] == esp_key and x["proc_base"] == clean_proc_base(target_proc))
                ),
                None,
            )
            if found:
                if proc_str:
                    found["procedimento"] = proc_str
                    found["proc_base"] = proc_b
                if s.medico_responsavel:
                    found["medico_responsavel"] = resolve_medico_cc(s.medico_responsavel)
                    found["medico_raw"] = s.medico_responsavel
                if s.swallis:
                    found["swalis"] = normalize_swalis(s.swallis)
                if getattr(s, "lateralidade", None):
                    found["lateralidade"] = normalize_lateralidade(s.lateralidade)
                if s.judicializado:
                    found["judicializado"] = normalize_judicializado(s.judicializado)
        elif s.tipo == "EXCLUIR":
            excluded_by_esp_pront[(esp_key, pront)] = {
                "id": s.id,
                "procedimento": proc_str,
                "data_criacao": s.data_criacao or "—",
                "usuario": s.usuario or "Gestão LEC",
                "detalhes": s.detalhes or "",
            }
            if pront in active_by_pront:
                active_by_pront[pront] = [
                    x
                    for x in active_by_pront[pront]
                    if not (
                        (s.id and x["sol_id"] == s.id)
                        or (x["esp_key"] == esp_key and x["procedimento"] == proc_str)
                    )
                ]

    active_esp_keys = {
        item["esp_key"]
        for plist in active_by_pront.values()
        for item in plist
    }
    cc_registered_esp_keys = active_esp_keys

    cc_by_esp: Dict[str, Dict[str, Any]] = {}
    for esp_k in cc_registered_esp_keys:
        cc_by_esp[esp_k] = {"pronts": set(), "rows_by_pront": {}, "total_linhas": 0}

    for pront, plist in active_by_pront.items():
        for item in plist:
            ek = item["esp_key"]
            bucket = cc_by_esp.setdefault(ek, {"pronts": set(), "rows_by_pront": {}, "total_linhas": 0})
            bucket["pronts"].add(pront)
            bucket["rows_by_pront"].setdefault(pront, []).append(item)
            bucket["total_linhas"] += 1

    return {
        "cc_registered_esp_keys": cc_registered_esp_keys,
        "cc_by_esp": cc_by_esp,
        "active_by_pront": active_by_pront,
        "pac_name_map": pac_name_map,
        "excluded_by_esp_pront": excluded_by_esp_pront,
        "pending_by_esp_pront": pending_by_esp_pront,
    }


def _medicos_equivalentes(med_cc: str, med_lec: str) -> bool:
    """Compara o nome do médico no CC com o nome na planilha do Sistema LEC."""
    c = strip_accents_upper(med_cc)
    l = strip_accents_upper(med_lec)
    vazio = {"", "—", "-", "NAO INFORMADO", "NAO_INFORMADO", "NONE"}
    if c in vazio and l in vazio:
        return True
    if c == l:
        return True
    # Caso em um dos lados ainda esteja no formato nome.sobrenome
    if "." in c and " " in l:
        tokens_c = [t for t in c.split(".") if t and not t.isdigit() and len(t) > 1]
        tokens_l = set(l.split())
        if tokens_c and all(any(tl.startswith(tc) for tl in tokens_l) for tc in tokens_c):
            return True
    return False


async def executar_e_salvar_diagnostico_lec(
    uploaded_files: List[Tuple[str, bytes]],
    app_db: AsyncSession,
    usuario_executor: str,
) -> Dict[str, Any]:
    """
    Processa os arquivos enviados (.xlsx/.xls/.zip), realiza a desduplicação e verificação
    preliminar de cobertura de especialidades, classifica todas as divergências (incluindo
    divergências cadastrais/clínicas de Swalis, Médico, Lateralidade e Judicialização) e salva
    o diagnóstico na tabela `diagnosticos_lec`.
    """
    excel_files = _extract_excel_files(uploaded_files)
    if not excel_files:
        raise ValueError("Nenhuma planilha Excel (.xlsx ou .xls) válida foi encontrada nos arquivos enviados.")

    parsed_sheets = []
    for fname, fbytes in excel_files:
        sheet_info = _parse_single_lec_excel(fname, fbytes)
        if sheet_info["total_linhas"] > 0:
            parsed_sheets.append(sheet_info)

    if not parsed_sheets:
        raise ValueError("As planilhas enviadas não contêm registros válidos de pacientes.")

    # 1. Desduplicação de planilhas repetidas da mesma fila bruta (raw_esp)
    by_raw_esp: Dict[str, List[Dict[str, Any]]] = {}
    for s in parsed_sheets:
        by_raw_esp.setdefault(s["raw_esp"], []).append(s)

    arquivos_duplicados: List[Dict[str, Any]] = []
    deduped_sheets: List[Dict[str, Any]] = []

    for raw_esp, group in by_raw_esp.items():
        if len(group) == 1:
            deduped_sheets.append(group[0])
            continue

        group_sorted = sorted(group, key=lambda x: x["total_linhas"], reverse=True)
        kept = group_sorted[0]
        seen_keys = {(r["prontuario"], r["proc_base"]) for r in kept["records"]}

        for dup in group_sorted[1:]:
            inter = len(kept["pronts_set"] & dup["pronts_set"])
            min_size = min(len(kept["pronts_set"]), len(dup["pronts_set"])) or 1
            overlap_ratio = inter / min_size

            if overlap_ratio >= 0.7:
                added_extra = 0
                for r in dup["records"]:
                    rk = (r["prontuario"], r["proc_base"])
                    if rk not in seen_keys:
                        seen_keys.add(rk)
                        kept["records"].append(r)
                        kept["pronts_set"].add(r["prontuario"])
                        added_extra += 1
                kept["total_linhas"] = len(kept["records"])
                arquivos_duplicados.append({
                    "arquivo_ignorado": dup["filename"],
                    "arquivo_mantido": kept["filename"],
                    "especialidade": kept["especialidade_display"],
                    "linhas_arquivo_ignorado": dup["total_linhas"],
                    "linhas_extras_consolidadas": added_extra,
                })
            else:
                deduped_sheets.append(dup)

        deduped_sheets.append(kept)

    # 2. Agrupar registros do Sistema LEC pela especialidade canônica (esp_key)
    lec_by_esp: Dict[str, Dict[str, Any]] = {}
    for sheet in deduped_sheets:
        for r in sheet["records"]:
            ek = r["esp_key"]
            bucket = lec_by_esp.setdefault(
                ek,
                {
                    "esp_key": ek,
                    "especialidade_display": get_display_specialty(ek),
                    "arquivos": [],
                    "pronts": set(),
                    "rows_by_pront": {},
                    "total_linhas": 0,
                },
            )
            if sheet["filename"] not in bucket["arquivos"]:
                bucket["arquivos"].append(sheet["filename"])
            bucket["pronts"].add(r["prontuario"])
            bucket["rows_by_pront"].setdefault(r["prontuario"], []).append(r)
            bucket["total_linhas"] += 1

    # 3. Reconstruir estado atual do Comunicação Cirúrgica
    cc_state = await _reconstruct_cc_state(app_db)
    cc_registered_esp_keys = cc_state["cc_registered_esp_keys"]
    cc_by_esp = cc_state["cc_by_esp"]
    pac_name_map = cc_state["pac_name_map"]
    excluded_by_esp_pront = cc_state["excluded_by_esp_pront"]
    pending_by_esp_pront = cc_state["pending_by_esp_pront"]

    # 4. Painel Preliminar de Cobertura de Especialidades
    lec_esp_keys = set(lec_by_esp.keys())
    esps_importadas_keys = sorted(lec_esp_keys & cc_registered_esp_keys)
    esps_sem_planilha_keys = sorted(cc_registered_esp_keys - lec_esp_keys)
    esps_nao_cadastradas_cc_keys = sorted(lec_esp_keys - cc_registered_esp_keys)

    cobertura_especialidades = {
        "total_cadastradas_cc": len(cc_registered_esp_keys),
        "total_importadas_no_diagnostico": len(esps_importadas_keys),
        "especialidades_importadas": [
            {
                "esp_key": k,
                "especialidade": get_display_specialty(k),
                "arquivos": lec_by_esp[k]["arquivos"],
                "linhas_lec": lec_by_esp[k]["total_linhas"],
                "prontuarios_lec": len(lec_by_esp[k]["pronts"]),
            }
            for k in esps_importadas_keys
        ],
        "especialidades_sem_planilha": [
            {
                "esp_key": k,
                "especialidade": get_display_specialty(k),
                "pacientes_ativos_cc": len(cc_by_esp.get(k, {}).get("pronts", set())),
            }
            for k in esps_sem_planilha_keys
        ],
        "especialidades_nao_cadastradas_no_cc": [
            {
                "esp_key": k,
                "especialidade": get_display_specialty(k),
                "arquivos": lec_by_esp[k]["arquivos"],
                "linhas_lec": lec_by_esp[k]["total_linhas"],
                "prontuarios_lec": len(lec_by_esp[k]["pronts"]),
            }
            for k in esps_nao_cadastradas_cc_keys
        ],
        "arquivos_duplicados": arquivos_duplicados,
    }

    # 5. Tabela Comparativa por Especialidade e Classificação das Divergências
    tabela_especialidades: List[Dict[str, Any]] = []
    divergencias: List[Dict[str, Any]] = []

    only_lec_by_esp: Dict[str, set] = {}
    only_cc_by_esp: Dict[str, set] = {}
    for ek in esps_importadas_keys:
        l_pronts = lec_by_esp[ek]["pronts"]
        c_pronts = cc_by_esp.get(ek, {}).get("pronts", set())
        only_lec_by_esp[ek] = l_pronts - c_pronts
        only_cc_by_esp[ek] = c_pronts - l_pronts

    cross_specialty_consumed_cc: set = set()

    for ek in sorted(lec_esp_keys):
        is_cadastrada_cc = ek in cc_registered_esp_keys
        l_bucket = lec_by_esp[ek]
        c_bucket = cc_by_esp.get(ek, {"pronts": set(), "rows_by_pront": {}, "total_linhas": 0})

        l_pronts = l_bucket["pronts"]
        c_pronts = c_bucket["pronts"]
        both_pronts = sorted(l_pronts & c_pronts)
        only_l = sorted(l_pronts - c_pronts)
        only_c = sorted(c_pronts - l_pronts)
        union_cnt = len(l_pronts | c_pronts) or 1
        perc = round((len(both_pronts) / union_cnt) * 100, 2) if is_cadastrada_cc else 0.0

        # 5A. Verificar Divergências de Informações (Swalis, Médico, Lateralidade, Judicialização)
        # para os pacientes que estão EM AMBOS os sistemas na mesma especialidade
        div_cadastral_esp_count = 0
        if is_cadastrada_cc:
            for pront in both_pronts:
                lec_rows = l_bucket["rows_by_pront"][pront]
                cc_rows = c_bucket["rows_by_pront"][pront]
                nome_pac = pac_name_map.get(pront)
                if not nome_pac or str(nome_pac).startswith("PACIENTE "):
                    nome_pac = lec_rows[0]["nome_paciente"]

                used_lec_indices = set()
                for c_idx, c_row in enumerate(cc_rows):
                    # Pareia pelo nome base do procedimento
                    matched_l_row = None
                    for l_idx, l_row in enumerate(lec_rows):
                        if l_idx not in used_lec_indices and l_row["proc_base"] == c_row["proc_base"]:
                            matched_l_row = l_row
                            used_lec_indices.add(l_idx)
                            break
                    if not matched_l_row and len(cc_rows) == 1 and len(lec_rows) == 1:
                        matched_l_row = lec_rows[0]
                    if not matched_l_row:
                        continue

                    campos_div = []
                    # 1. Swalis
                    if c_row["swalis"] != matched_l_row["swalis"]:
                        campos_div.append({
                            "campo": "Swalis",
                            "chave": "swalis",
                            "valor_cc": c_row["swalis"],
                            "valor_lec": matched_l_row["swalis"],
                        })
                    # 2. Médico Responsável
                    if not _medicos_equivalentes(c_row["medico_responsavel"], matched_l_row["medico_responsavel"]):
                        campos_div.append({
                            "campo": "Médico Responsável",
                            "chave": "medico_responsavel",
                            "valor_cc": c_row["medico_responsavel"],
                            "valor_lec": matched_l_row["medico_responsavel"],
                        })
                    # 3. Lateralidade
                    if c_row["lateralidade"] != matched_l_row["lateralidade"]:
                        campos_div.append({
                            "campo": "Lateralidade",
                            "chave": "lateralidade",
                            "valor_cc": c_row["lateralidade"],
                            "valor_lec": matched_l_row["lateralidade"],
                        })
                    # 4. Judicialização
                    if c_row["judicializado"] != matched_l_row["judicializado"]:
                        campos_div.append({
                            "campo": "Judicialização",
                            "chave": "judicializado",
                            "valor_cc": c_row["judicializado"],
                            "valor_lec": matched_l_row["judicializado"],
                        })

                    if campos_div:
                        div_cadastral_esp_count += 1
                        resumo_campos = "; ".join(
                            f"{cd['campo']} (CC: {cd['valor_cc']} | LEC: {cd['valor_lec']})"
                            for cd in campos_div
                        )
                        divergencias.append({
                            "item_id": f"DIV_INFO_{ek}_{pront}_{c_idx}",
                            "categoria": "DIVERGENCIA_DADOS_CADASTRAIS",
                            "origem_divergencia": "EM_AMBOS_DADOS_DIVERGENTES",
                            "prontuario": pront,
                            "nome_paciente": nome_pac,
                            "especialidade": get_display_specialty(ek),
                            "esp_key": ek,
                            "especialidade_secundaria": None,
                            "esp_key_secundaria": None,
                            "procedimento": c_row["procedimento"],
                            "procedimento_cc": c_row["procedimento"],
                            "medico_responsavel": c_row["medico_responsavel"],
                            "swalis": c_row["swalis"],
                            "lateralidade": c_row["lateralidade"],
                            "judicializado": c_row["judicializado"],
                            "campos_divergentes": campos_div,
                            "valores_atuais_cc": {
                                "swalis": c_row["swalis"],
                                "medico_responsavel": c_row["medico_responsavel"],
                                "lateralidade": c_row["lateralidade"],
                                "judicializado": c_row["judicializado"],
                            },
                            "valores_atuais_lec": {
                                "swalis": matched_l_row["swalis"],
                                "medico_responsavel": matched_l_row["medico_responsavel"],
                                "lateralidade": matched_l_row["lateralidade"],
                                "judicializado": matched_l_row["judicializado"],
                            },
                            "data_referencia": c_row["data_criacao"],
                            "detalhes_status": f"Divergência de informações: {resumo_campos}",
                            "solicitacao_id_cc": c_row["sol_id"],
                            "acao_sugerida_cc": "EDITAR_INFORMACOES_NO_CC",
                            "sincronizado_no_cc": False,
                            "data_sincronizacao": None,
                            "usuario_sincronizacao": None,
                        })

        tabela_especialidades.append({
            "esp_key": ek,
            "especialidade": get_display_specialty(ek),
            "cadastrada_no_cc": is_cadastrada_cc,
            "arquivos": l_bucket["arquivos"],
            "lec_linhas": l_bucket["total_linhas"],
            "lec_prontuarios": len(l_pronts),
            "cc_linhas": c_bucket["total_linhas"],
            "cc_prontuarios": len(c_pronts),
            "em_ambos": len(both_pronts),
            "so_no_lec": len(only_l),
            "so_no_cc": len(only_c),
            "divergencias_info": div_cadastral_esp_count,
            "percentual_sincronia": perc,
        })

        if not is_cadastrada_cc:
            continue

        # 5B. Analisar cada paciente que está SÓ NO SISTEMA LEC nesta especialidade
        for pront in only_l:
            lec_rows = l_bucket["rows_by_pront"][pront]
            first_lec = lec_rows[0]
            nome_pac = pac_name_map.get(pront)
            if not nome_pac or str(nome_pac).startswith("PACIENTE "):
                nome_pac = first_lec["nome_paciente"]
            procs_lec_str = " / ".join(dict.fromkeys(r["procedimento"] for r in lec_rows))

            other_cc_esp_key = None
            other_cc_row = None
            for cand_ek, cand_only_c_set in only_cc_by_esp.items():
                if cand_ek != ek and pront in cand_only_c_set:
                    other_cc_esp_key = cand_ek
                    other_cc_row = cc_by_esp[cand_ek]["rows_by_pront"][pront][0]
                    break

            if other_cc_esp_key and other_cc_row:
                cross_specialty_consumed_cc.add((other_cc_esp_key, pront))
                divergencias.append({
                    "item_id": f"OUTRA_ESP_{ek}_{other_cc_esp_key}_{pront}",
                    "categoria": "EM_OUTRA_ESPECIALIDADE_NO_CC",
                    "origem_divergencia": "AMBOS_ESPECIALIDADE_DIFERENTE",
                    "prontuario": pront,
                    "nome_paciente": nome_pac,
                    "especialidade": get_display_specialty(ek),
                    "esp_key": ek,
                    "especialidade_secundaria": get_display_specialty(other_cc_esp_key),
                    "esp_key_secundaria": other_cc_esp_key,
                    "procedimento": procs_lec_str,
                    "procedimento_cc": other_cc_row["procedimento"],
                    "medico_responsavel": first_lec["medico_responsavel"],
                    "swalis": first_lec["swalis"],
                    "lateralidade": first_lec["lateralidade"],
                    "judicializado": first_lec["judicializado"],
                    "campos_divergentes": [
                        {
                            "campo": "Especialidade",
                            "chave": "especialidade",
                            "valor_cc": get_display_specialty(other_cc_esp_key),
                            "valor_lec": get_display_specialty(ek),
                        }
                    ],
                    "data_referencia": first_lec["data_indicacao"],
                    "detalhes_status": (
                        f"Na planilha do Sistema LEC está em {get_display_specialty(ek)}, "
                        f"mas no Comunicação Cirúrgica está ativo em {get_display_specialty(other_cc_esp_key)} "
                        f"(Solicitação {other_cc_row['sol_id']} de {other_cc_row['data_criacao']})."
                    ),
                    "solicitacao_id_cc": other_cc_row["sol_id"],
                    "acao_sugerida_cc": "TRANSFERIR_ESPECIALIDADE_NO_CC",
                    "sincronizado_no_cc": False,
                    "data_sincronizacao": None,
                    "usuario_sincronizacao": None,
                })
                continue

            excl_info = excluded_by_esp_pront.get((ek, pront))
            if excl_info:
                divergencias.append({
                    "item_id": f"EXCL_PEND_LEC_{ek}_{pront}",
                    "categoria": "EXCLUSAO_APROVADA_CC_PENDENTE_LEC",
                    "origem_divergencia": "SO_NO_LEC",
                    "prontuario": pront,
                    "nome_paciente": nome_pac,
                    "especialidade": get_display_specialty(ek),
                    "esp_key": ek,
                    "especialidade_secundaria": None,
                    "esp_key_secundaria": None,
                    "procedimento": procs_lec_str,
                    "procedimento_cc": excl_info["procedimento"],
                    "medico_responsavel": first_lec["medico_responsavel"],
                    "swalis": first_lec["swalis"],
                    "lateralidade": first_lec["lateralidade"],
                    "judicializado": first_lec["judicializado"],
                    "campos_divergentes": [],
                    "data_referencia": excl_info["data_criacao"],
                    "detalhes_status": (
                        f"Exclusão já aprovada no CC em {excl_info['data_criacao']} "
                        f"por {excl_info['usuario']} (ID {excl_info['id']}). Pendente de exclusão no Sistema LEC."
                    ),
                    "solicitacao_id_cc": excl_info["id"],
                    "acao_sugerida_cc": "NENHUMA_ACAO_NO_CC",
                    "sincronizado_no_cc": False,
                    "data_sincronizacao": None,
                    "usuario_sincronizacao": None,
                })
                continue

            pend_info = pending_by_esp_pront.get((ek, pront))
            if pend_info:
                divergencias.append({
                    "item_id": f"PEND_CC_{ek}_{pront}",
                    "categoria": "SOLICITACAO_PENDENTE_NO_CC",
                    "origem_divergencia": "SO_NO_LEC",
                    "prontuario": pront,
                    "nome_paciente": nome_pac,
                    "especialidade": get_display_specialty(ek),
                    "esp_key": ek,
                    "especialidade_secundaria": None,
                    "esp_key_secundaria": None,
                    "procedimento": procs_lec_str,
                    "procedimento_cc": pend_info["procedimento"],
                    "medico_responsavel": first_lec["medico_responsavel"],
                    "swalis": first_lec["swalis"],
                    "lateralidade": first_lec["lateralidade"],
                    "judicializado": first_lec["judicializado"],
                    "campos_divergentes": [],
                    "data_referencia": pend_info["data_criacao"],
                    "detalhes_status": (
                        f"Possui solicitação {pend_info['tipo']} PENDENTE de aprovação no CC "
                        f"desde {pend_info['data_criacao']}."
                    ),
                    "solicitacao_id_cc": pend_info["id"],
                    "acao_sugerida_cc": "INCLUIR_NO_CC",
                    "sincronizado_no_cc": False,
                    "data_sincronizacao": None,
                    "usuario_sincronizacao": None,
                })
                continue

            divergencias.append({
                "item_id": f"DIRETO_LEC_{ek}_{pront}",
                "categoria": "INSERIDO_DIRETO_NO_LEC",
                "origem_divergencia": "SO_NO_LEC",
                "prontuario": pront,
                "nome_paciente": nome_pac,
                "especialidade": get_display_specialty(ek),
                "esp_key": ek,
                "especialidade_secundaria": None,
                "esp_key_secundaria": None,
                "procedimento": procs_lec_str,
                "procedimento_cc": None,
                "medico_responsavel": first_lec["medico_responsavel"],
                "swalis": first_lec["swalis"],
                "lateralidade": first_lec["lateralidade"],
                "judicializado": first_lec["judicializado"],
                "campos_divergentes": [],
                "data_referencia": first_lec["data_indicacao"],
                "detalhes_status": (
                    f"Cadastrado diretamente no Sistema LEC (Indicação: {first_lec['data_indicacao_original']}) "
                    f"sem solicitação de inclusão no Comunicação Cirúrgica."
                ),
                "solicitacao_id_cc": None,
                "acao_sugerida_cc": "INCLUIR_NO_CC",
                "sincronizado_no_cc": False,
                "data_sincronizacao": None,
                "usuario_sincronizacao": None,
            })

    # 5C. Analisar cada paciente que está SÓ NO COMUNICAÇÃO CIRÚRGICA nas especialidades importadas
    for ek in esps_importadas_keys:
        c_bucket = cc_by_esp.get(ek, {"pronts": set(), "rows_by_pront": {}, "total_linhas": 0})
        l_pronts = lec_by_esp[ek]["pronts"]
        only_c = sorted(c_bucket["pronts"] - l_pronts)

        for pront in only_c:
            if (ek, pront) in cross_specialty_consumed_cc:
                continue

            cc_rows = c_bucket["rows_by_pront"][pront]
            first_cc = cc_rows[0]
            nome_pac = pac_name_map.get(pront) or f"PACIENTE {pront}"
            procs_cc_str = " / ".join(dict.fromkeys(r["procedimento"] for r in cc_rows))

            is_import_fila = all(r["is_importacao_fila"] for r in cc_rows)
            det_lower = (first_cc["detalhes"] or "").lower()
            is_teste = "teste" in det_lower or pront == 10000016

            if is_import_fila or is_teste:
                motivo_txt = (
                    "Registro de teste ativo no Comunicação Cirúrgica e ausente no Sistema LEC."
                    if is_teste
                    else f"Veio de importação anterior ({first_cc['sol_id']}) e já saiu do Sistema LEC (operado ou excluído no LEC), sem exclusão no CC."
                )
                divergencias.append({
                    "item_id": f"SAIU_LEC_{ek}_{pront}",
                    "categoria": "SAIU_DO_LEC_SEM_BAIXA_NO_CC",
                    "origem_divergencia": "SO_NO_CC",
                    "prontuario": pront,
                    "nome_paciente": nome_pac,
                    "especialidade": get_display_specialty(ek),
                    "esp_key": ek,
                    "especialidade_secundaria": None,
                    "esp_key_secundaria": None,
                    "procedimento": procs_cc_str,
                    "procedimento_cc": procs_cc_str,
                    "medico_responsavel": first_cc["medico_responsavel"],
                    "swalis": first_cc["swalis"],
                    "lateralidade": first_cc["lateralidade"],
                    "judicializado": first_cc["judicializado"],
                    "campos_divergentes": [],
                    "data_referencia": first_cc["data_criacao"],
                    "detalhes_status": motivo_txt,
                    "solicitacao_id_cc": first_cc["sol_id"],
                    "acao_sugerida_cc": "EXCLUIR_DO_CC",
                    "sincronizado_no_cc": False,
                    "data_sincronizacao": None,
                    "usuario_sincronizacao": None,
                })
            else:
                divergencias.append({
                    "item_id": f"INCL_PEND_LEC_{ek}_{pront}",
                    "categoria": "INCLUSAO_APROVADA_CC_PENDENTE_LEC",
                    "origem_divergencia": "SO_NO_CC",
                    "prontuario": pront,
                    "nome_paciente": nome_pac,
                    "especialidade": get_display_specialty(ek),
                    "esp_key": ek,
                    "especialidade_secundaria": None,
                    "esp_key_secundaria": None,
                    "procedimento": procs_cc_str,
                    "procedimento_cc": procs_cc_str,
                    "medico_responsavel": first_cc["medico_responsavel"],
                    "swalis": first_cc["swalis"],
                    "lateralidade": first_cc["lateralidade"],
                    "judicializado": first_cc["judicializado"],
                    "campos_divergentes": [],
                    "data_referencia": first_cc["data_criacao"],
                    "detalhes_status": (
                        f"Inclusão aprovada no CC em {first_cc['data_criacao']} "
                        f"(Solicitação {first_cc['sol_id']}), mas ainda não consta na planilha do Sistema LEC."
                    ),
                    "solicitacao_id_cc": first_cc["sol_id"],
                    "acao_sugerida_cc": "EXCLUIR_DO_CC",
                    "sincronizado_no_cc": False,
                    "data_sincronizacao": None,
                    "usuario_sincronizacao": None,
                })

    # 6. Calcular resumo global
    pronts_lec_importadas = set()
    pronts_cc_importadas = set()
    for ek in esps_importadas_keys:
        pronts_lec_importadas |= lec_by_esp[ek]["pronts"]
        pronts_cc_importadas |= cc_by_esp.get(ek, {}).get("pronts", set())

    em_ambos_global = len(pronts_lec_importadas & pronts_cc_importadas)
    uniao_global = len(pronts_lec_importadas | pronts_cc_importadas) or 1
    perc_global = round((em_ambos_global / uniao_global) * 100, 2)

    contagem_categorias = {
        "EXCLUSAO_APROVADA_CC_PENDENTE_LEC": sum(
            1 for d in divergencias if d["categoria"] == "EXCLUSAO_APROVADA_CC_PENDENTE_LEC"
        ),
        "INCLUSAO_APROVADA_CC_PENDENTE_LEC": sum(
            1 for d in divergencias if d["categoria"] == "INCLUSAO_APROVADA_CC_PENDENTE_LEC"
        ),
        "EM_OUTRA_ESPECIALIDADE_NO_CC": sum(
            1 for d in divergencias if d["categoria"] == "EM_OUTRA_ESPECIALIDADE_NO_CC"
        ),
        "DIVERGENCIA_DADOS_CADASTRAIS": sum(
            1 for d in divergencias if d["categoria"] == "DIVERGENCIA_DADOS_CADASTRAIS"
        ),
        "INSERIDO_DIRETO_NO_LEC": sum(
            1 for d in divergencias if d["categoria"] == "INSERIDO_DIRETO_NO_LEC"
        ),
        "SAIU_DO_LEC_SEM_BAIXA_NO_CC": sum(
            1 for d in divergencias if d["categoria"] == "SAIU_DO_LEC_SEM_BAIXA_NO_CC"
        ),
        "SOLICITACAO_PENDENTE_NO_CC": sum(
            1 for d in divergencias if d["categoria"] == "SOLICITACAO_PENDENTE_NO_CC"
        ),
    }

    diag_id = f"DIAG-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    arquivos_nomes = [s["filename"] for s in parsed_sheets]

    resumo_obj = {
        "id": diag_id,
        "data_criacao": now_str,
        "usuario": usuario_executor,
        "total_arquivos_enviados": len(parsed_sheets),
        "total_arquivos_duplicados": len(arquivos_duplicados),
        "especialidades_importadas_count": len(esps_importadas_keys),
        "especialidades_cadastradas_cc_count": len(cc_registered_esp_keys),
        "especialidades_sem_planilha_count": len(esps_sem_planilha_keys),
        "especialidades_nao_cadastradas_cc_count": len(esps_nao_cadastradas_cc_keys),
        "prontuarios_unicos_lec": len(pronts_lec_importadas),
        "prontuarios_unicos_cc": len(pronts_cc_importadas),
        "prontuarios_em_ambos": em_ambos_global,
        "percentual_sincronia_global": perc_global,
        "total_divergencias": len(divergencias),
        "total_sincronizados_no_cc": 0,
        "contagem_categorias": contagem_categorias,
    }

    detalhes_obj = {
        "cobertura_especialidades": cobertura_especialidades,
        "tabela_especialidades": tabela_especialidades,
        "divergencias": divergencias,
    }

    novo_diag = DiagnosticoLec(
        id=diag_id,
        data_criacao=now_str,
        usuario=usuario_executor,
        arquivos_json=json.dumps(arquivos_nomes, ensure_ascii=False),
        resumo_json=json.dumps(resumo_obj, ensure_ascii=False),
        detalhes_json=json.dumps(detalhes_obj, ensure_ascii=False),
    )
    app_db.add(novo_diag)
    await app_db.commit()

    return {
        **resumo_obj,
        "arquivos_nomes": arquivos_nomes,
        **detalhes_obj,
    }


async def listar_diagnosticos_lec(app_db: AsyncSession) -> List[Dict[str, Any]]:
    """Lista os diagnósticos realizados da data/hora mais recente para a mais antiga."""
    stmt = select(
        DiagnosticoLec.id,
        DiagnosticoLec.data_criacao,
        DiagnosticoLec.usuario,
        DiagnosticoLec.arquivos_json,
        DiagnosticoLec.resumo_json,
    ).order_by(desc(DiagnosticoLec.data_criacao), desc(DiagnosticoLec.id))
    res = await app_db.execute(stmt)
    rows = res.all()

    result = []
    for r in rows:
        try:
            resumo = json.loads(r.resumo_json or "{}")
        except Exception:
            resumo = {}
        try:
            arquivos = json.loads(r.arquivos_json or "[]")
        except Exception:
            arquivos = []

        result.append({
            "id": r.id,
            "data_criacao": r.data_criacao,
            "usuario": r.usuario,
            "arquivos_nomes": arquivos,
            **resumo,
        })
    return result


async def obter_diagnostico_lec(diagnostico_id: str, app_db: AsyncSession) -> Optional[Dict[str, Any]]:
    """Obtém os detalhes completos de um diagnóstico realizado."""
    stmt = select(DiagnosticoLec).where(DiagnosticoLec.id == diagnostico_id)
    res = await app_db.execute(stmt)
    diag = res.scalars().first()
    if not diag:
        return None

    try:
        resumo = json.loads(diag.resumo_json or "{}")
    except Exception:
        resumo = {}
    try:
        detalhes = json.loads(diag.detalhes_json or "{}")
    except Exception:
        detalhes = {}
    try:
        arquivos = json.loads(diag.arquivos_json or "[]")
    except Exception:
        arquivos = []

    return {
        "id": diag.id,
        "data_criacao": diag.data_criacao,
        "usuario": diag.usuario,
        "arquivos_nomes": arquivos,
        **resumo,
        **detalhes,
    }


async def sincronizar_itens_diagnostico_no_cc(
    diagnostico_id: str,
    item_ids: List[str],
    acao_override: Optional[str],
    dados_edicao: Optional[Dict[str, Any]],
    app_db: AsyncSession,
    aghu_db: Optional[AsyncSession],
    usuario_executor: str,
    perfil_executor: str = "Gestão LEC",
) -> Dict[str, Any]:
    """
    Executa ações de sincronização e correção manual exclusivamente no banco de dados do
    Comunicação Cirúrgica, registrando todas as mudanças no menu Histórico com
    `origem_menu = "Pacientes"`, `evento_tipo = "EXECUCAO"`, o usuário executor e detalhes
    completos (sendo mudanças de especialidade ou de informações gravadas como `tipo = "EDITAR"`
    do tipo `"EXECUCAO"`).
    """
    stmt = select(DiagnosticoLec).where(DiagnosticoLec.id == diagnostico_id)
    res = await app_db.execute(stmt)
    diag = res.scalars().first()
    if not diag:
        raise ValueError("Diagnóstico não encontrado.")

    resumo = json.loads(diag.resumo_json or "{}")
    detalhes = json.loads(diag.detalhes_json or "{}")
    divergencias: List[Dict[str, Any]] = detalhes.get("divergencias", [])

    target_set = set(item_ids)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sincronizados_agora = 0

    res_pac = await app_db.execute(select(Paciente))
    existing_pacientes = {p.codigo: p for p in res_pac.scalars().all() if p.codigo is not None}

    res_sol = await app_db.execute(select(Solicitacao))
    all_sols = res_sol.scalars().all()
    sols_by_pront: Dict[int, List[Solicitacao]] = {}
    for s in all_sols:
        if s.codigo_paciente:
            sols_by_pront.setdefault(int(s.codigo_paciente), []).append(s)

    for item in divergencias:
        if item.get("item_id") not in target_set:
            continue
        if item.get("sincronizado_no_cc"):
            continue

        acao = acao_override or item.get("acao_sugerida_cc")
        if acao == "DAR_BAIXA_NO_CC":
            acao = "EXCLUIR_DO_CC"

        pront = int(item["prontuario"])
        esp_display = item["especialidade"]
        esp_key = item.get("esp_key") or normalize_lec_specialty_key(esp_display)
        proc_str = item.get("procedimento") or "PROCEDIMENTO NÃO ESPECIFICADO"
        nome_pac = item.get("nome_paciente") or f"PACIENTE {pront}"
        lat_val = normalize_lateralidade(item.get("lateralidade"))

        if acao == "INCLUIR_NO_CC":
            nome_social_pac = None
            if aghu_db:
                try:
                    q_pac = text("SELECT nome, nome_social FROM agh.aip_pacientes WHERE prontuario = :p LIMIT 1")
                    r_pac = await aghu_db.execute(q_pac, {"p": pront})
                    row_aghu = r_pac.mappings().first()
                    if row_aghu:
                        nome_social_pac = row_aghu.get("nome_social")
                        if row_aghu.get("nome") or nome_social_pac:
                            nome_pac = resolver_nome_paciente(row_aghu.get("nome"), nome_social_pac)
                except Exception:
                    pass

            if pront not in existing_pacientes:
                new_p = Paciente(
                    codigo=pront,
                    nome=nome_pac,
                    especialidade=esp_display,
                    procedimento=proc_str,
                    lateralidade=lat_val,
                )
                app_db.add(new_p)
                existing_pacientes[pront] = new_p

            sol_id = f"SOL-FILA-SYNC-{pront}-{uuid.uuid4().hex[:6]}"
            dth_ind = item.get("data_referencia")
            new_sol = Solicitacao(
                id=sol_id,
                tipo="INSERIR",
                especialidade=esp_display,
                procedimento=proc_str,
                codigo_paciente=pront,
                nome_paciente=nome_pac,
                judicializado=item.get("judicializado") or "Não",
                swallis=item.get("swalis") if item.get("swalis") != "—" else "",
                medico_responsavel=item.get("medico_responsavel") or "Não informado",
                lateralidade=lat_val,
                detalhes=(
                    f"Inclusão no Comunicação Cirúrgica realizada via Diagnóstico CC x Sistema LEC "
                    f"(#{diagnostico_id}): paciente constava ativo na planilha do Sistema LEC "
                    f"(Indicação: {dth_ind or '—'})."
                ),
                status="APROVADO",
                data_criacao=now_str,
                usuario=usuario_executor,
                perfil_executor=perfil_executor,
                origem_menu="Pacientes",
                evento_tipo="EXECUCAO",
            )
            app_db.add(new_sol)
            sols_by_pront.setdefault(pront, []).append(new_sol)

            item["sincronizado_no_cc"] = True
            item["data_sincronizacao"] = now_str
            item["usuario_sincronizacao"] = usuario_executor
            sincronizados_agora += 1

        elif acao == "EXCLUIR_DO_CC":
            procs_to_exclude = [p.strip() for p in proc_str.split(" / ") if p.strip()] or [proc_str]
            for p_single in procs_to_exclude:
                excl_sol = Solicitacao(
                    id=uuid.uuid4().hex[:8],
                    tipo="EXCLUIR",
                    especialidade=esp_display,
                    procedimento=p_single,
                    codigo_paciente=pront,
                    nome_paciente=nome_pac,
                    judicializado=item.get("judicializado") or "Não",
                    swallis=item.get("swalis") if item.get("swalis") != "—" else "",
                    medico_responsavel=item.get("medico_responsavel") or "Não informado",
                    lateralidade=lat_val,
                    detalhes=(
                        f"Exclusão do Comunicação Cirúrgica realizada via Diagnóstico CC x Sistema LEC "
                        f"(#{diagnostico_id}): paciente não consta mais na fila ativa do Sistema LEC."
                    ),
                    status="APROVADO",
                    data_criacao=now_str,
                    usuario=usuario_executor,
                    perfil_executor=perfil_executor,
                    origem_menu="Pacientes",
                    evento_tipo="EXECUCAO",
                )
                app_db.add(excl_sol)

            item["sincronizado_no_cc"] = True
            item["data_sincronizacao"] = now_str
            item["usuario_sincronizacao"] = usuario_executor
            sincronizados_agora += 1

        elif acao == "TRANSFERIR_ESPECIALIDADE_NO_CC":
            esp_antiga_display = item.get("especialidade_secundaria") or "GERAL"
            esp_antiga_key = item.get("esp_key_secundaria") or normalize_lec_specialty_key(esp_antiga_display)
            proc_cc_str = item.get("procedimento_cc") or proc_str

            p_sols = sols_by_pront.get(pront, [])
            for s in p_sols:
                if normalize_lec_specialty_key(s.especialidade) == esp_antiga_key:
                    s.especialidade = esp_display

            if pront in existing_pacientes:
                pac_obj = existing_pacientes[pront]
                if normalize_lec_specialty_key(pac_obj.especialidade) == esp_antiga_key:
                    pac_obj.especialidade = esp_display

            # Registra no menu Histórico (origem_menu = 'Pacientes') como Edição (EDITAR) do tipo Execução (EXECUCAO)
            edit_esp_sol = Solicitacao(
                id=uuid.uuid4().hex[:8],
                tipo="EDITAR",
                especialidade=esp_display,
                procedimento=proc_cc_str,
                procedimento_anterior=proc_cc_str,
                codigo_paciente=pront,
                nome_paciente=nome_pac,
                judicializado=item.get("judicializado") or "Não",
                swallis=item.get("swalis") if item.get("swalis") != "—" else "",
                medico_responsavel=item.get("medico_responsavel") or "Não informado",
                lateralidade=lat_val,
                detalhes=(
                    f"Especialidade: {esp_antiga_display} -> {esp_display} | "
                    f"Justificativa: Alteração de especialidade realizada via Diagnóstico Comunicação Cirúrgica x Sistema LEC (#{diagnostico_id})."
                ),
                status="APROVADO",
                data_criacao=now_str,
                usuario=usuario_executor,
                perfil_executor=perfil_executor,
                origem_menu="Pacientes",
                evento_tipo="EXECUCAO",
            )
            app_db.add(edit_esp_sol)

            item["sincronizado_no_cc"] = True
            item["data_sincronizacao"] = now_str
            item["usuario_sincronizacao"] = usuario_executor
            sincronizados_agora += 1

        elif acao == "EDITAR_INFORMACOES_NO_CC":
            ed = dados_edicao or {}
            atuais_cc = item.get("valores_atuais_cc") or {
                "swalis": item.get("swalis") or "—",
                "medico_responsavel": item.get("medico_responsavel") or "Não informado",
                "lateralidade": item.get("lateralidade") or "Indefinida",
                "judicializado": item.get("judicializado") or "Não",
            }

            novo_swalis = normalize_swalis(ed.get("swalis", atuais_cc["swalis"]))
            novo_medico = (ed.get("medico_responsavel") or atuais_cc["medico_responsavel"] or "Não informado").strip().upper()
            nova_lat = normalize_lateralidade(ed.get("lateralidade", atuais_cc["lateralidade"]))
            novo_jud = normalize_judicializado(ed.get("judicializado", atuais_cc["judicializado"]))
            just_extra = (ed.get("justificativa") or "").strip()

            mudancas_txt = []
            if novo_swalis != atuais_cc["swalis"]:
                mudancas_txt.append(f"Swalis (Priorização): {atuais_cc['swalis']} -> {novo_swalis}")
            if strip_accents_upper(novo_medico) != strip_accents_upper(atuais_cc["medico_responsavel"]):
                mudancas_txt.append(f"Médico Responsável: {atuais_cc['medico_responsavel']} -> {novo_medico}")
            if nova_lat != atuais_cc["lateralidade"]:
                mudancas_txt.append(f"Lateralidade: {atuais_cc['lateralidade']} -> {nova_lat}")
            if novo_jud != atuais_cc["judicializado"]:
                mudancas_txt.append(f"Judicialização: {atuais_cc['judicializado']} -> {novo_jud}")

            if not mudancas_txt:
                mudancas_txt.append("Verificação manual de informações sem alteração de valores")

            justificativa_final = (
                f"Correção manual de informações divergentes realizada via Diagnóstico Comunicação Cirúrgica x Sistema LEC (#{diagnostico_id})"
            )
            if just_extra:
                justificativa_final += f" — {just_extra}"

            edit_info_sol = Solicitacao(
                id=uuid.uuid4().hex[:8],
                tipo="EDITAR",
                especialidade=esp_display,
                procedimento=proc_str,
                procedimento_anterior=proc_str,
                codigo_paciente=pront,
                nome_paciente=nome_pac,
                judicializado=novo_jud,
                swallis=novo_swalis if novo_swalis != "—" else "",
                medico_responsavel=novo_medico,
                lateralidade=nova_lat,
                detalhes=f"{'; '.join(mudancas_txt)} | Justificativa: {justificativa_final}",
                status="APROVADO",
                data_criacao=now_str,
                usuario=usuario_executor,
                perfil_executor=perfil_executor,
                origem_menu="Pacientes",
                evento_tipo="EXECUCAO",
            )
            app_db.add(edit_info_sol)

            if pront in existing_pacientes:
                existing_pacientes[pront].lateralidade = nova_lat

            item["valores_atuais_cc"] = {
                "swalis": novo_swalis,
                "medico_responsavel": novo_medico,
                "lateralidade": nova_lat,
                "judicializado": novo_jud,
            }
            item["sincronizado_no_cc"] = True
            item["data_sincronizacao"] = now_str
            item["usuario_sincronizacao"] = usuario_executor
            sincronizados_agora += 1

    try:
        from ..providers.implementations.paciente_hybrid_provider import invalidate_paciente_cache
        invalidate_paciente_cache()
    except Exception:
        pass

    total_sync = sum(1 for d in divergencias if d.get("sincronizado_no_cc"))
    resumo["total_sincronizados_no_cc"] = total_sync
    detalhes["divergencias"] = divergencias

    diag.resumo_json = json.dumps(resumo, ensure_ascii=False)
    diag.detalhes_json = json.dumps(detalhes, ensure_ascii=False)

    await app_db.commit()

    return {
        "sincronizados_agora": sincronizados_agora,
        "total_sincronizados_no_cc": total_sync,
        "diagnostico": {
            "id": diag.id,
            "data_criacao": diag.data_criacao,
            "usuario": diag.usuario,
            "arquivos_nomes": json.loads(diag.arquivos_json or "[]"),
            **resumo,
            **detalhes,
        },
    }
