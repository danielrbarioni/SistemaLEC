import sqlite3
import os

def clear_tables():
    db_path = "data/app.db"
    if not os.path.exists(db_path):
        print(f"Banco de dados local {db_path} não encontrado.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Limpar tabelas solicitacoes, pacientes e status_locais
        cursor.execute("DELETE FROM solicitacoes;")
        print("Tabela 'solicitacoes' limpa localmente.")
        cursor.execute("DELETE FROM pacientes;")
        print("Tabela 'pacientes' limpa localmente.")
        cursor.execute("DELETE FROM status_locais;")
        print("Tabela 'status_locais' limpa localmente.")
        conn.commit()
        print("Commit realizado com sucesso localmente.")
    except Exception as e:
        conn.rollback()
        print(f"Erro ao limpar banco de dados local: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    clear_tables()
