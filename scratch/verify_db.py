import sqlite3

conn = sqlite3.connect('data/app.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tabelas no app.db copiado:", tables)

for table in tables:
    t_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {t_name}")
    count = cursor.fetchone()[0]
    print(f" - {t_name}: {count} registros")

conn.close()
