import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

stdin, stdout, stderr = ssh.exec_command("""python3 -c "
import sqlite3
db_path = '/var/app/sistemalec/data/app.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('''
    SELECT id, tipo, data_criacao, codigo_paciente, nome_paciente, detalhes 
    FROM solicitacoes 
    WHERE data_criacao LIKE '%2026-07-31%' 
       OR data_criacao LIKE '%31/07/2026%'
''')
rows = c.fetchall()
print(f'Solicitações encontradas para 31/07/2026: {len(rows)}')
for r in rows:
    print(' ', r)

conn.close()
" """)

print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
