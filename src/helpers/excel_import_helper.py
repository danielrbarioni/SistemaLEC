# src/helpers/excel_import_helper.py

import io
import re
import unicodedata
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from ..models.user import User
from ..models.profile import Profile
from ..models.paciente import Paciente
from ..models.solicitacao import Solicitacao
from ..helpers.string_helper import generate_profile_id, remove_accents


def normalize_col_name(text: Any) -> str:
    """Normaliza o nome da coluna removendo acentos, caracteres especiais e convertendo para minúsculas."""
    if not isinstance(text, str):
        return ""
    text_norm = unicodedata.normalize("NFD", text)
    text_norm = re.sub(r"[\u0300-\u036f]", "", text_norm)
    return text_norm.lower().strip().replace(" ", "_")


def clean_cell_value(val: Any) -> Optional[str]:
    """Limpa e formata o valor de uma célula da planilha."""
    if pd.isna(val) or val is None:
        return None
    # Se for datetime ou Timestamp do pandas, formata adequadamente
    if hasattr(val, "strftime"):
        try:
            return val.strftime("%Y-%m-%d %H:%M")
        except Exception:
            pass
    val_str = str(val).strip()
    if val_str.endswith(".0"):
        val_str = val_str[:-2]
    return val_str if val_str else None


async def process_excel_pacientes_import(
    file_bytes: bytes,
    app_db: AsyncSession,
    aghu_db: Optional[AsyncSession],
    usuario_executor: str,
    especialidade_override: Optional[str] = None
) -> Dict[str, Any]:
    """
    Processa uma planilha Excel contendo filas de pacientes por especialidade.
    Utiliza estratégias de pré-carregamento em memória para máxima performance e resiliência a cabeçalhos.
    """
    excel_stream = io.BytesIO(file_bytes)
    df = None
    last_err = None

    # Tenta ordenadamente com openpyxl (.xlsx), xlrd (.xls) e o padrão do pandas
    for engine in ["openpyxl", "xlrd", None]:
        try:
            excel_stream.seek(0)
            if engine:
                df = pd.read_excel(excel_stream, header=0, engine=engine)
            else:
                df = pd.read_excel(excel_stream, header=0)
            break
        except Exception as err:
            last_err = err

    if df is None:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não foi possível interpretar o arquivo Excel enviado. Certifique-se de que é uma planilha Excel (.xlsx ou .xls) válida. (Erro: {last_err})"
        )

    total_linhas = len(df)
    solicitacoes_criadas = 0
    solicitacoes_atualizadas = 0
    novos_medicos = []
    erros = []

    # 0. Mapeamento flexível de colunas por nome normalizado
    col_idx_map = {}
    for i, c in enumerate(df.columns):
        norm = normalize_col_name(c)
        if norm:
            col_idx_map[norm] = i

    def get_col_val(row_vals: list, col_names: List[str], fallback_idx: int) -> Optional[str]:
        for name in col_names:
            if name in col_idx_map:
                idx = col_idx_map[name]
                if idx < len(row_vals):
                    return clean_cell_value(row_vals[idx])
        if fallback_idx < len(row_vals):
            return clean_cell_value(row_vals[fallback_idx])
        return None

    # 1. Carregar caches em memória para performance em lote (Zero N+1 DB Queries)
    procedimentos_cache = {}
    
    # Perfis existentes indexados por ID e por nome/especialidade normalizados
    res_profiles = await app_db.execute(select(Profile))
    all_db_profiles = res_profiles.scalars().all()
    existing_profiles: Dict[str, Profile] = {}
    for p in all_db_profiles:
        if p.id:
            existing_profiles[p.id] = p
        if p.especialidade:
            norm_key = remove_accents(p.especialidade).strip().upper()
            existing_profiles[norm_key] = p
        if p.nome:
            norm_nome = remove_accents(p.nome).strip().upper()
            existing_profiles[norm_nome] = p

    # Usuários existentes (indexados por username e perfil_id para compatibilidade multi-especialidade)
    res_users = await app_db.execute(select(User))
    existing_users = {(u.username.lower(), u.perfil_id): u for u in res_users.scalars().all() if u.username}

    # Pacientes existentes
    res_pacientes = await app_db.execute(select(Paciente))
    existing_pacientes = {p.codigo: p for p in res_pacientes.scalars().all() if p.codigo is not None}

    # Solicitações existentes
    res_solic = await app_db.execute(select(Solicitacao))
    existing_solic_list = res_solic.scalars().all()
    existing_solicitacoes = {}
    existing_solic_by_key = {}

    for s in existing_solic_list:
        if s.id:
            existing_solicitacoes[s.id] = s
        if s.codigo_paciente:
            try:
                p_code = int(s.codigo_paciente)
                key = (p_code, s.procedimento or "")
                existing_solic_by_key[key] = s
            except (ValueError, TypeError):
                pass

    for idx, row in df.iterrows():
        linha_num = idx + 2  # Considera cabeçalho na linha 1

        cols = list(row.values)
        if len(cols) < 2:
            erros.append(f"Linha {linha_num}: Linha com estrutura incompleta.")
            continue

        raw_id_fila = get_col_val(cols, ["id_fila", "id_fila_sistema", "idfila"], 0)
        raw_prontuario = get_col_val(cols, ["prontuario", "cod_prontuario", "pront"], 1)
        raw_id_procedimento = get_col_val(cols, ["id_procedimento", "id_proc", "procedimento_id"], 2)
        raw_medico_responsavel = get_col_val(cols, ["medico_responsavel", "medico", "crm"], 3)
        raw_id_motivo_status = get_col_val(cols, ["id_motivo_status", "motivo_status"], 6)
        raw_id_especialidade = get_col_val(cols, ["id_especialidade", "id_esp", "especialidade_id"], 8)
        raw_swalis = get_col_val(cols, ["swalis", "swallis", "prioridade_swalis"], 9)
        raw_sin_judicializado = get_col_val(cols, ["sin_judicializado", "judicializado"], 10)
        raw_dth_indicacao = get_col_val(cols, ["dth_indicacao", "data_indicacao", "dth_indicacao_fila"], 11)

        if not raw_prontuario or not raw_prontuario.isdigit():
            erros.append(f"Linha {linha_num}: Prontuário inválido ou ausente ({raw_prontuario}).")
            continue

        prontuario_int = int(raw_prontuario)
        id_procedimento_int = int(raw_id_procedimento) if raw_id_procedimento and raw_id_procedimento.isdigit() else None
        id_especialidade_int = int(raw_id_especialidade) if raw_id_especialidade and raw_id_especialidade.isdigit() else None

        # Resolução de Nome do Procedimento e Especialidade no AGHU ou Fallback (sempre padronizado em CAIXA ALTA)
        if especialidade_override:
            nome_especialidade = especialidade_override.strip().upper()
        else:
            nome_especialidade = f"ESPECIALIDADE {id_especialidade_int}" if id_especialidade_int else "GERAL"

        nome_procedimento = f"PROCEDIMENTO {id_procedimento_int}" if id_procedimento_int else "PROCEDIMENTO NÃO ESPECIFICADO"

        if aghu_db and id_procedimento_int and id_especialidade_int:
            cache_key = (id_procedimento_int, id_especialidade_int)
            if cache_key in procedimentos_cache:
                proc_cached, esp_cached = procedimentos_cache[cache_key]
                nome_procedimento = proc_cached
                if not especialidade_override:
                    nome_especialidade = esp_cached.strip().upper()
            else:
                try:
                    query_aghu = text("""
                        SELECT 
                            pci.descricao AS proc_desc,
                            esp.nome_especialidade AS esp_nome
                        FROM agh.mbc_procedimento_cirurgicos pci
                        LEFT JOIN agh.mbc_especialidade_proc_cirgs epr ON pci.seq = epr.pci_seq
                        LEFT JOIN agh.agh_especialidades esp ON epr.esp_seq = esp.seq 
                        WHERE pci.seq = :id_proc AND esp.seq = :id_esp
                        LIMIT 1
                    """)
                    res = await aghu_db.execute(query_aghu, {"id_proc": id_procedimento_int, "id_esp": id_especialidade_int})
                    row_aghu = res.mappings().first()
                    if row_aghu:
                        proc_desc = row_aghu.get("proc_desc") or nome_procedimento
                        esp_nome = row_aghu.get("esp_nome") or nome_especialidade
                        nome_procedimento = f"{proc_desc} (ID {id_procedimento_int})"
                        if not especialidade_override:
                            nome_especialidade = esp_nome.strip().upper()
                        procedimentos_cache[cache_key] = (nome_procedimento, nome_especialidade)
                except Exception as e:
                    print(f"Erro ao buscar procedimento {id_procedimento_int} no AGHU: {e}")

        # Garantir existência do Perfil da Especialidade no SQLite local usando ID canônico limpo
        canonical_perfil_id = generate_profile_id(nome_especialidade)
        norm_esp_key = remove_accents(nome_especialidade).strip().upper()

        target_profile = existing_profiles.get(canonical_perfil_id) or existing_profiles.get(norm_esp_key)
        if not target_profile:
            target_profile = Profile(
                id=canonical_perfil_id,
                nome=nome_especialidade.upper(),
                tipo="ESPECIALIDADE",
                cor="verde",
                especialidade=nome_especialidade.upper()
            )
            app_db.add(target_profile)
            existing_profiles[canonical_perfil_id] = target_profile
            existing_profiles[norm_esp_key] = target_profile
            existing_profiles[target_profile.nome] = target_profile

        perfil_id = target_profile.id
        nome_especialidade = target_profile.especialidade or target_profile.nome or nome_especialidade.upper()

        # Garantir existência do Médico Responsável
        medico_username = raw_medico_responsavel or "NAO_INFORMADO"
        if medico_username != "NAO_INFORMADO":
            medico_clean = medico_username.strip()
            medico_lower = medico_clean.lower()
            user_key = (medico_lower, perfil_id)

            if user_key not in existing_users:
                new_doctor = User(
                    username=medico_clean,
                    nome=medico_clean,
                    perfil_id=perfil_id,
                    especialidade=nome_especialidade.upper(),
                    funcao="Médico"
                )
                app_db.add(new_doctor)
                existing_users[user_key] = new_doctor
                novos_medicos.append({
                    "username": medico_clean,
                    "especialidade": nome_especialidade.upper()
                })

        # Garantir registro do Paciente (AGHU ou SQLite Local)
        nome_paciente = f"PACIENTE {prontuario_int}"
        if prontuario_int not in existing_pacientes:
            if aghu_db:
                try:
                    query_pac = text("""
                        SELECT nome 
                        FROM agh.aip_pacientes 
                        WHERE prontuario = :prontuario
                        LIMIT 1
                    """)
                    res_pac = await aghu_db.execute(query_pac, {"prontuario": prontuario_int})
                    row_pac = res_pac.mappings().first()
                    if row_pac and row_pac.get("nome"):
                        nome_paciente = row_pac["nome"]
                except Exception as e:
                    print(f"Erro ao buscar paciente {prontuario_int} no AGHU: {e}")

            new_pac = Paciente(
                codigo=prontuario_int,
                nome=nome_paciente,
                especialidade=nome_especialidade,
                procedimento=nome_procedimento
            )
            app_db.add(new_pac)
            existing_pacientes[prontuario_int] = new_pac
        else:
            nome_paciente = existing_pacientes[prontuario_int].nome or nome_paciente

        # Tratar judicialização
        is_judicializado = "Não"
        if raw_sin_judicializado:
            raw_jud_upper = raw_sin_judicializado.upper()
            if raw_jud_upper in ["S", "SIM", "1", "TRUE", "V", "VERDADEIRO"]:
                is_judicializado = "Sim"

        swalis_val = raw_swalis or ""
        dth_indicacao_str = raw_dth_indicacao or datetime.now().strftime("%Y-%m-%d %H:%M")

        # ID único da solicitação
        solic_id = f"SOL-FILA-{raw_id_fila or idx+1}-{prontuario_int}"
        detalhes_str = f"Importação de fila via planilha Excel. ID Fila: {raw_id_fila or 'N/A'}. Motivo Status: {raw_id_motivo_status or 'N/A'}. Indicação: {dth_indicacao_str}."

        existing_solic = None
        proc_key = (prontuario_int, nome_procedimento)

        if solic_id in existing_solicitacoes:
            existing_solic = existing_solicitacoes[solic_id]
        elif proc_key in existing_solic_by_key:
            existing_solic = existing_solic_by_key[proc_key]

        if existing_solic:
            existing_solic.procedimento = nome_procedimento
            existing_solic.especialidade = nome_especialidade
            existing_solic.medico_responsavel = medico_username
            existing_solic.swallis = swalis_val
            existing_solic.judicializado = is_judicializado
            existing_solic.detalhes = detalhes_str
            solicitacoes_atualizadas += 1
        else:
            new_solic = Solicitacao(
                id=solic_id,
                tipo="INSERIR",
                especialidade=nome_especialidade,
                procedimento=nome_procedimento,
                codigo_paciente=prontuario_int,
                nome_paciente=nome_paciente,
                judicializado=is_judicializado,
                swallis=swalis_val,
                medico_responsavel=medico_username,
                detalhes=detalhes_str,
                status="APROVADO",
                data_criacao=dth_indicacao_str,
                usuario=usuario_executor,
                perfil_executor="Gestão LEC",
                origem_menu="Pacientes",
                evento_tipo="EXECUCAO"
            )
            app_db.add(new_solic)
            existing_solicitacoes[solic_id] = new_solic
            existing_solic_by_key[proc_key] = new_solic
            solicitacoes_criadas += 1

    # Commit em lote ao final para máxima velocidade
    await app_db.commit()

    return {
        "total_linhas": total_linhas,
        "solicitacoes_criadas": solicitacoes_criadas,
        "solicitacoes_atualizadas": solicitacoes_atualizadas,
        "novos_medicos": novos_medicos,
        "erros": erros
    }
