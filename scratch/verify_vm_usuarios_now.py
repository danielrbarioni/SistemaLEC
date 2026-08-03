import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

stdin, stdout, stderr = ssh.exec_command("""python3 -c "
import sqlite3
db_path = '/var/app/sistemalec/data/app.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('SELECT username, nome, perfil_id, especialidade FROM usuarios')
rows = cursor.fetchall()
print(f'Total de usuários no SQLite da VM ({db_path}): {len(rows)}')
for r in rows:
    print(' ', r)
conn.close()
" """)

print("Diagnostico direto na VM:\n", stdout.read().decode('utf-8', errors='replace'))
ssh.close()
