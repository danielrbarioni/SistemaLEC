import sqlite3

def check():
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()
    tables = [t[0] for t in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print("Tabelas encontradas no app.db local:", tables)
    for t in tables:
        if not t.startswith("sqlite_"):
            count = cursor.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f" - Tabela '{t}': {count} registros")
    conn.close()

if __name__ == "__main__":
    check()
