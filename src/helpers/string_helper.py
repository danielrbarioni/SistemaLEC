import unicodedata
import re

def remove_accents(text: str) -> str:
    """
    Remove acentos de uma string.
    """
    if not text:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def normalize_specialty_name(name: str) -> str:
    """
    Normaliza nomes de especialidades cirúrgicas.
    Unifica CIRURGIA GERAL, APARELHO DIGESTIVO e PROCTOLOGIA (e variações) para GERAL.
    """
    if not name:
        return ""
    clean = name.strip()
    norm = remove_accents(clean).upper().strip()
    if norm in [
        "CIRURGIA GERAL",
        "CIRURGIA_GERAL",
        "APARELHO DIGESTIVO",
        "APARELHO_DIGESTIVO",
        "CIRURGIA DO APARELHO DIGESTIVO",
        "CIRURGIA_DO_APARELHO_DIGESTIVO",
        "PROCTOLOGIA",
        "GERAL",
    ]:
        return "GERAL"
    return clean.upper()

def generate_profile_id(name_or_specialty: str) -> str:
    """
    Gera um identificador de perfil limpo, sem acentos, em caixa alta e usando underscores.
    Ex: 'Cirurgia Plástica' -> 'CIRURGIA_PLASTICA'
    Ex: 'Cirurgia Geral' -> 'GERAL'
    """
    norm_spec = normalize_specialty_name(name_or_specialty)
    clean = remove_accents(norm_spec).upper().strip()
    clean = re.sub(r'[^A-Z0-9_]+', '_', clean)
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean or "PERFIL"

def resolver_nome_paciente(nome: str | None, nome_social: str | None = None) -> str:
    """
    Retorna o nome do paciente priorizando o nome social cadastrado no AGHU,
    acrescentando a indicação '(Nome Social)' de forma idempotente.
    """
    social_clean = str(nome_social).strip() if nome_social is not None else ""
    if social_clean and social_clean.lower() not in ("none", "null", "—", "-"):
        if "(nome social)" in social_clean.lower():
            return social_clean
        return f"{social_clean} (Nome Social)"
    nome_clean = str(nome).strip() if nome is not None else ""
    return nome_clean

def aplicar_nome_social_dict(pac: dict) -> dict:
    """
    Atualiza o dicionário do paciente para substituir 'nome' pelo nome social
    formatado quando 'nome_social' existir e não for vazio, definindo também
    'possui_nome_social'.
    """
    if not pac:
        return pac
    nome_orig = pac.get("nome")
    nome_soc = pac.get("nome_social")
    social_clean = str(nome_soc).strip() if nome_soc is not None else ""
    has_social = bool(social_clean and social_clean.lower() not in ("none", "null", "—", "-"))
    if has_social:
        pac["nome"] = resolver_nome_paciente(nome_orig, social_clean)
        pac["nome_social"] = social_clean
        pac["possui_nome_social"] = True
    else:
        already_flagged = "(nome social)" in str(nome_orig or "").lower()
        pac["possui_nome_social"] = bool(pac.get("possui_nome_social") or already_flagged)
    return pac

def normalizar_nome_base_procedimento(proc: str | None) -> str:
    """
    Extrai o nome base canônico do procedimento cirúrgico sem o sufixo '(ID XXX)',
    sem prefixos numéricos 'XXX - ', sem acentos e em caixa alta, para comparação
    exata da dupla paciente + procedimento.
    """
    if not proc:
        return ""
    s = str(proc).strip()
    s = re.sub(r'\s*\(\s*(?:ID\s*)?\d+\s*\)$', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s*[-–—]\s*(?:ID\s*)?\d+$', '', s, flags=re.IGNORECASE)
    s = re.sub(r'^\d+\s*[-–—]\s*', '', s)
    s = remove_accents(s).upper().strip()
    s = re.sub(r'\s+', ' ', s)
    return s
