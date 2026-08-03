import paramiko
import os

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=15)

local_db = os.path.abspath('data/app.db')
remote_db = '/var/app/sistemalec/data/app.db'

print(f"Parando o serviço sistemalec na VM...")
ssh.exec_command("systemctl stop sistemalec")

print(f"Enviando banco correto ({local_db}) para a VM ({remote_db})...")
sftp = ssh.open_sftp()
sftp.put(local_db, remote_db)
sftp.close()

print("Verificando conteúdo do banco na VM após upload:")
cmd = """python3 -c "
import sqlite3
conn = sqlite3.connect('/var/app/sistemalec/data/app.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM usuarios')
u_cnt = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM solicitacoes')
s_cnt = c.fetchone()[0]
print(f'=== SUCESSO: Banco da VM agora possui {u_cnt} usuários e {s_cnt} solicitações! ===')
c.execute('SELECT username, nome FROM usuarios')
for u in sorted(c.fetchall(), key=lambda x: str(x[0]).lower()):
    print('  ', u)
conn.close()
" """

stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode('utf-8', errors='replace'))

print("Reiniciando o serviço sistemalec na VM...")
ssh.exec_command("systemctl start sistemalec")

ssh.close()
print("Processo concluído com sucesso!")
