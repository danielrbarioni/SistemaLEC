import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

sftp = ssh.open_sftp()
local_db = r"c:\Users\daniel.barioni\.gemini\antigravity-ide\scratch\Antigravity IDE\Sistema LEC\data\app.db"
remote_db = "/var/app/sistemalec/data/app.db"

sftp.put(local_db, remote_db)
sftp.close()

stdin, stdout, stderr = ssh.exec_command("""python3 -c "
import sqlite3
db_path = '/var/app/sistemalec/data/app.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Garantir exclusao dos IDs de 24/07/2026 no banco restaurado
cursor.execute(\\\"DELETE FROM solicitacoes WHERE id IN ('c9fc59fd', '4d482c98') OR data_criacao LIKE '%2026-07-24%' OR data_criacao LIKE '%24/07/2026%'\\\")
conn.commit()

cursor.execute('SELECT COUNT(*) FROM usuarios')
print('Total de usuários no banco da VM pós-upload:', cursor.fetchone()[0])
cursor.execute('SELECT username, nome FROM usuarios LIMIT 5')
print('Primeiros usuários:', cursor.fetchall())
conn.close()
" """)

print("Upload do banco com os usuários:\n", stdout.read().decode('utf-8', errors='replace'))
ssh.close()
