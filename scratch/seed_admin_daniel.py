import sqlite3
import os

DB_PATH = 'data/app.db'

def seed():
    print(f"Connecting to database: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print(f"WARNING: Database file {DB_PATH} does not exist.")
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Inserir o perfil ADMIN se não existir
    print("Checking if ADMIN profile exists in 'perfis'...")
    cursor.execute("SELECT id FROM perfis WHERE id = 'ADMIN'")
    profile_exists = cursor.fetchone()
    
    if not profile_exists:
        print("Inserting ADMIN profile...")
        cursor.execute(
            "INSERT INTO perfis (id, nome, tipo, cor, especialidade) VALUES (?, ?, ?, ?, ?)",
            ('ADMIN', 'Administrador', 'ADMIN', 'azul', None)
        )
    else:
        print("ADMIN profile already exists.")

    # 2. Inserir o usuário daniel.barioni se não existir
    print("Checking if user daniel.barioni exists in 'usuarios'...")
    cursor.execute("SELECT id FROM usuarios WHERE username = 'daniel.barioni'")
    user_exists = cursor.fetchone()

    if not user_exists:
        print("Inserting user daniel.barioni...")
        cursor.execute(
            "INSERT INTO usuarios (username, nome, perfil_id, especialidade) VALUES (?, ?, ?, ?)",
            ('daniel.barioni', 'Daniel Barioni', 'ADMIN', None)
        )
    else:
        print("User daniel.barioni already exists.")

    conn.commit()
    conn.close()
    print("Seed process completed.")

if __name__ == '__main__':
    seed()
