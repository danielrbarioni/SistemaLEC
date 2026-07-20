import sqlite3

conn = sqlite3.connect('data/app.db')
cursor = conn.cursor()

try:
    cursor.execute("DROP TABLE IF EXISTS solicitacoes_criacao_usuario")
    print("Dropped solicitacoes_criacao_usuario table if it existed.")
except Exception as e:
    print(f"Error dropping table: {e}")

try:
    # SQLite doesn't easily support dropping a column in older versions, but let's check if we need to.
    # Let's inspect the columns of usuarios table.
    cursor.execute("PRAGMA table_info(usuarios)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'funcao' in columns:
        print("funcao column exists in usuarios.")
        # To drop a column in SQLite >= 3.35.0, we can do ALTER TABLE ... DROP COLUMN.
        cursor.execute("ALTER TABLE usuarios DROP COLUMN funcao")
        print("Dropped funcao column.")
except Exception as e:
    print(f"Error checking/dropping funcao column: {e}")

conn.commit()
conn.close()
