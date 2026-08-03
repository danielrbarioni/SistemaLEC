import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

sftp = ssh.open_sftp()
remote_path = "/var/app/sistemalec/data/app.db"
local_path = r"c:\Users\daniel.barioni\.gemini\antigravity-ide\scratch\Antigravity IDE\Sistema LEC\data\app.db"

sftp.get(remote_path, local_path)
sftp.close()
ssh.close()

print(f"Banco de dados de {remote_path} copiado com sucesso para {local_path}!")
