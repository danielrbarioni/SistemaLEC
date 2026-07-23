import sqlite3

def dump_db():
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()
    
    print("=== PERFIS ===")
    for row in cursor.execute("SELECT id, nome, tipo, especialidade FROM perfis").fetchall():
        print(row)
        
    print("\n=== SOLICITACOES ===")
    columns = [desc[0] for desc in cursor.execute("SELECT * FROM solicitacoes LIMIT 1").description]
    print("Colunas:", columns)
    for row in cursor.execute("SELECT * FROM solicitacoes").fetchall():
        print(row)
        
    print("\n=== USUARIOS ===")
    for row in cursor.execute("SELECT id, username, nome, perfil_id FROM usuarios").fetchall():
        print(row)
        
    conn.close()

if __name__ == "__main__":
    dump_db()
