import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

sftp = ssh.open_sftp()
local_db = r"c:\Users\daniel.barioni\.gemini\antigravity-ide\scratch\Antigravity IDE\Sistema LEC\data\app.db"
remote_db = "/var/app/sistemalec/data/app.db"

# Para o serviço primeiro para evitar qualquer trava de arquivo no SQLite
stdin, stdout, stderr = ssh.exec_command("systemctl stop sistemalec")
stdout.read()

# Transfere o arquivo app.db do localhost para a VM
sftp.put(local_db, remote_db)
sftp.close()

# Deleta as solicitações de 24/07/2026 e verifica a contagem exata de usuários
stdin, stdout, stderr = ssh.exec_command("""python3 -c "
import sqlite3
conn = sqlite3.connect('/var/app/sistemalec/data/app.db')
c = conn.cursor()
c.execute(\\\"DELETE FROM solicitacoes WHERE id IN ('c9fc59fd', '4d482c98') OR data_criacao LIKE '%2026-07-24%' OR data_criacao LIKE '%24/07/2026%'\\\")
conn.commit()

c.execute('SELECT username, nome FROM usuarios')
rows = c.fetchall()
print('=== USUÁRIOS APÓS PARAR SERVIÇO E FAZER UPLOAD:', len(rows))
for r in sorted(rows, key=lambda x: x[0].lower()):
    print(' ', r)
conn.close()
" """)

print(stdout.read().decode('utf-8', errors='replace'))

# Inicia o serviço novamente
stdin, stdout, stderr = ssh.exec_command("systemctl start sistemalec")
stdout.read()

ssh.close()
