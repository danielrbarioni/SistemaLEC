import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

stdin, stdout, stderr = ssh.exec_command("""python3 -c "
import sqlite3
for db_path in ['/var/app/sistemalec/data/app.db', '/var/app/sistemalec/app.db']:
    print('=== BANCO:', db_path)
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT username, nome, perfil_id FROM usuarios')
        rows = cursor.fetchall()
        print(f'Total de usuários em {db_path}: {len(rows)}')
        for r in rows:
            print(' ', r)
        conn.close()
    except Exception as e:
        print('Erro:', e)
" """)

print("Diagnostico de usuarios na VM:\n", stdout.read().decode('utf-8', errors='replace'))
ssh.close()
