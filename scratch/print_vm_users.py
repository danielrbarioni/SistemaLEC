import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

stdin, stdout, stderr = ssh.exec_command("""python3 -c "
import sqlite3
db_path = '/var/app/sistemalec/data/app.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('SELECT username, nome FROM usuarios')
rows = c.fetchall()
print('=== USUÁRIOS NO BANCO DA VM:', len(rows))
for r in sorted(rows, key=lambda x: x[0].lower()):
    print(' ', r)
conn.close()
" """)

print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
