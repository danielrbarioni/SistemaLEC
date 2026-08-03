import sqlite3

conn = sqlite3.connect('data/app.db')
cursor = conn.cursor()
cursor.execute("INSERT OR REPLACE INTO perfis (id, nome, tipo, cor, especialidade) VALUES ('OBSERVADOR', 'OBSERVADOR', 'OBSERVADOR', 'cinza', NULL)")
conn.commit()
print("Perfil OBSERVADOR cadastrado com sucesso na tabela perfis!")

cursor.execute("SELECT id, nome, tipo FROM perfis")
print("Perfis cadastrados:", cursor.fetchall())
conn.close()
