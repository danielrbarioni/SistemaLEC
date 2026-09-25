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
    Unifica CIRURGIA GERAL (e variações) para GERAL.
    """
    if not name:
        return ""
    clean = name.strip()
    norm = remove_accents(clean).upper().strip()
    if norm in ["CIRURGIA GERAL", "CIRURGIA_GERAL", "GERAL"]:
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

