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

def generate_profile_id(name_or_specialty: str) -> str:
    """
    Gera um identificador de perfil limpo, sem acentos, em caixa alta e usando underscores.
    Ex: 'Cirurgia Plástica' -> 'CIRURGIA_PLASTICA'
    """
    clean = remove_accents(name_or_specialty).upper().strip()
    clean = re.sub(r'[^A-Z0-9_]+', '_', clean)
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean or "PERFIL"
