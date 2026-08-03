from fastapi.testclient import TestClient
from src.main import app
from src.auth.auth import auth_handler

client = TestClient(app)

def test_observador_role_fallback_and_permissions():
    user_info = {
        "username": "usuario_sem_perfil_teste",
        "displayName": ["Usuario Sem Perfil"],
        "groups": ["OBSERVADOR", "Users"]
    }
    
    token = auth_handler.create_access_token(user_info)
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "tipo": "SOLICITACAO",
        "especialidade": "Cardiologia",
        "procedimento": "Teste",
        "codigo_paciente": "12345",
        "nome_paciente": "Paciente Teste",
        "judicializado": "Não",
        "detalhes": "Teste de permissão para perfil OBSERVADOR"
    }
    
    response = client.post("/api/solicitacoes", json=payload, headers=headers)
    assert response.status_code == 403, f"Expected 403 Forbidden but got {response.status_code}: {response.text}"
    print("✓ TESTE 1: Tentativa de criar solicitação como OBSERVADOR bloqueada com 403 Forbidden.")
    
    response_get = client.get("/api/solicitacoes", headers=headers)
    assert response_get.status_code == 200, f"Expected 200 OK for GET but got {response_get.status_code}"
    print("✓ TESTE 2: Consulta de solicitações como OBSERVADOR autorizada com 200 OK (somente leitura).")

if __name__ == "__main__":
    test_observador_role_fallback_and_permissions()
