import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

stdin, stdout, stderr = ssh.exec_command("""python3 -c "
import os
print('Diretório de trabalho do processo ou serviço:')
for path in ['/var/app/sistemalec', '/root/sistema-lec', '/var/app/sistemalec/data', '/root']:
    if os.path.exists(path):
        print('=== PATH:', path)
        for f in os.listdir(path):
            if f.endswith('.db'):
                full = os.path.join(path, f)
                import sqlite3
                conn = sqlite3.connect(full)
                c = conn.cursor()
                try:
                    c.execute('SELECT COUNT(*) FROM usuarios')
                    cnt = c.fetchone()[0]
                    print(f'   - {full}: {cnt} usuarios')
                except Exception as e:
                    print(f'   - {full}: erro {e}')
                conn.close()
" """)

print("Diagnostico completo de bancos na VM:\n", stdout.read().decode('utf-8', errors='replace'))
ssh.close()
