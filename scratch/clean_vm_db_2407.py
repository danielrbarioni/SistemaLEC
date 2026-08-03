import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

stdin, stdout, stderr = ssh.exec_command("""python3 -c "
import sqlite3
db_path = '/var/app/sistemalec/data/app.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar registros do dia 2026-07-24 antes da exclusao
cursor.execute(\\\"SELECT id, tipo, data_criacao FROM solicitacoes WHERE data_criacao LIKE '2026-07-24%' OR data_criacao LIKE '24/07/2026%'\\\")
rows = cursor.fetchall()
print(f'Registros encontrados para 24/07/2026: {len(rows)}')
for r in rows:
    print(' ', r)

# Excluir solicitacoes e respostas feitas no dia 24/07/2026
cursor.execute(\\\"DELETE FROM solicitacoes WHERE data_criacao LIKE '2026-07-24%' OR data_criacao LIKE '24/07/2026%'\\\")
deleted_count = cursor.rowcount
conn.commit()
print(f'Registros excluidos com sucesso: {deleted_count}')

conn.close()
" """)

print("Output da exclusao no banco da VM:\n", stdout.read().decode())
print("Error:\n", stderr.read().decode())
ssh.close()
