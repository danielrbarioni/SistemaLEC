import paramiko
import os
from dotenv import load_dotenv

load_dotenv()

hostname = os.getenv("LEC_VM_HOST")
username = os.getenv("LEC_VM_USER")
password = os.getenv("LEC_VM_PASSWORD")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username=username, password=password)

# Consulta tabela de pacientes
stdin, stdout, stderr = ssh.exec_command("cd /var/app/sistemalec && /root/.local/bin/uv run python -c \"import sqlite3; conn = sqlite3.connect('data/app.db'); print('Pacientes:', conn.execute('SELECT codigo, nome FROM pacientes').fetchall())\"")
print(stdout.read().decode('utf-8'))

# Consulta tabela de solicitacoes
stdin, stdout, stderr = ssh.exec_command("cd /var/app/sistemalec && /root/.local/bin/uv run python -c \"import sqlite3; conn = sqlite3.connect('data/app.db'); print('Solicitações:', conn.execute('SELECT id, codigo_paciente, nome_paciente FROM solicitacoes').fetchall())\"")
print(stdout.read().decode('utf-8'))

ssh.close()
