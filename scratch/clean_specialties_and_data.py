import sqlite3
import os

def clean_database():
    db_path = "data/app.db"
    if not os.path.exists(db_path):
        print(f"Banco de dados local {db_path} não encontrado.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # 1. Limpar solicitações, pacientes e status_locais
        cursor.execute("DELETE FROM solicitacoes;")
        print("Tabela 'solicitacoes' limpa.")
        cursor.execute("DELETE FROM pacientes;")
        print("Tabela 'pacientes' limpa.")
        cursor.execute("DELETE FROM status_locais;")
        print("Tabela 'status_locais' limpa.")

        # 2. Excluir perfis do tipo ESPECIALIDADE
        cursor.execute("DELETE FROM perfis WHERE tipo = 'ESPECIALIDADE';")
        print("Perfis de especialidades excluídos.")

        # 3. Remover usuários e solicitações de criação associados aos perfis excluídos
        cursor.execute("DELETE FROM usuarios WHERE perfil_id NOT IN (SELECT id FROM perfis);")
        print("Usuários associados às especialidades excluídos.")

        cursor.execute("DELETE FROM solicitacoes_criacao_usuario WHERE perfil_id NOT IN (SELECT id FROM perfis);")
        print("Solicitações de criação de usuário associadas às especialidades excluídas.")

        conn.commit()
        print("\nExclusão realizada com sucesso!")
    except Exception as e:
        conn.rollback()
        print(f"Erro ao limpar banco de dados: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    clean_database()
