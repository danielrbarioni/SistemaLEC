import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

stdin, stdout, stderr = ssh.exec_command("""python3 -c "
import sqlite3, os
print('Diretório atual:', os.getcwd())
for path in ['/var/app/sistemalec/data/app.db', '/var/app/sistemalec/app.db']:
    if os.path.exists(path):
        conn = sqlite3.connect(path)
        print('=== Banco:', path)
        for t in conn.execute(\\\"SELECT name FROM sqlite_master WHERE type='table';\\\").fetchall():
            cnt = conn.execute(f'SELECT COUNT(*) FROM {t[0]}').fetchone()[0]
            print(f'Tabela {t[0]}: {cnt} registros')
" """)
print("Output:\n", stdout.read().decode())
print("Error:\n", stderr.read().decode())

ssh.close()
