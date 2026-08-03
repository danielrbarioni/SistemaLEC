import sqlite3

conn = sqlite3.connect('data/app.db')
cursor = conn.cursor()
cursor.execute("SELECT id, nome, tipo, cor, especialidade FROM perfis")
rows = cursor.fetchall()
print("Perfis no banco de dados:")
for row in rows:
    print(row)
conn.close()
