import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

cmd = """python3 -c "
import sqlite3
for target in ['/var/app/sistemalec/data/app.db', '/var/app/sistemalec/data/app.db.bak']:
    try:
        conn = sqlite3.connect(target)
        c = conn.cursor()
        c.execute('SELECT username, nome FROM usuarios')
        users = c.fetchall()
        c.execute('SELECT COUNT(*) FROM solicitacoes')
        solic_cnt = c.fetchone()[0]
        print(f'=== TARGET: {target} (Users: {len(users)}, Solicitacoes: {solic_cnt})')
        for u in sorted(users, key=lambda x: str(x[0]).lower()):
            print('  ', u)
        conn.close()
    except Exception as e:
        print(f'=== TARGET: {target} Erro: {e}')
" """

stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
