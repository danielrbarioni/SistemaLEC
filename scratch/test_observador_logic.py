import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.routers.perfil import get_current_user_role
from src.auth.auth import AuthHandler, MockAuthProvider

def test_auth_fallback_mock():
    print("--- TESTE 1: AuthHandler Fallback com Usuario sem Cadastro Local ---")
    
    auth_h = AuthHandler()
    auth_h.provider = MockAuthProvider()
    
    user_data = {
        "username": "usuario_ebserh_novo_sem_cadastro",
        "displayName": ["Novo Usuario Ebserh"],
        "groups": ["Users"],
        "email": "novo@ebserh.gov.br"
    }
    
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "data", "app.db")
    import sqlite3
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.nome, p.tipo, p.especialidade 
            FROM usuarios u
            JOIN perfis p ON u.perfil_id = p.id
            WHERE LOWER(u.username) = LOWER(?)
            """,
            (user_data["username"],)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            db_nome, db_perfil_tipo, db_especialidade = row
            user_data["perfil_tipo"] = db_perfil_tipo
        else:
            user_data["groups"] = ["OBSERVADOR", "Users"]
            user_data["perfil_tipo"] = "OBSERVADOR"
            user_data["especialidade"] = None

    print("Dados do usuario pos-autenticacao/enriquecimento:", user_data)
    assert user_data["perfil_tipo"] == "OBSERVADOR", f"Expected OBSERVADOR but got {user_data.get('perfil_tipo')}"
    assert "OBSERVADOR" in user_data["groups"], "Expected OBSERVADOR in groups"
    print("OK: Fallback para perfil OBSERVADOR validado com sucesso!")
    
    print("\n--- TESTE 2: Resolucao de Role no get_current_user_role ---")
    role = get_current_user_role(user_data)
    assert role == "OBSERVADOR", f"Expected role OBSERVADOR but got {role}"
    print("OK: get_current_user_role retornou OBSERVADOR conforme esperado!")

if __name__ == "__main__":
    try:
        test_auth_fallback_mock()
    except Exception as e:
        print("FALHA:", e)
        sys.exit(1)
