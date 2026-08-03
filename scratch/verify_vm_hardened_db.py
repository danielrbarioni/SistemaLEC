import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

cmd = """python3 -c "
import sqlite3
conn = sqlite3.connect('/var/lib/sistemalec/app.db')
c = conn.cursor()
u_cnt = len(c.execute('SELECT username FROM usuarios').fetchall())
s_cnt = c.execute('SELECT COUNT(*) FROM solicitacoes').fetchone()[0]
print(f'=== VERIFICAÇÃO FINAL VM ===')
print(f'   -> BANCO ISOLADO (/var/lib/sistemalec/app.db): {u_cnt} usuários e {s_cnt} solicitações.')
conn.close()
" """

stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
