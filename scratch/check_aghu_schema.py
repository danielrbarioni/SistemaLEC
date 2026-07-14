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

# Upload do check_aghu.py
sftp = ssh.open_sftp()
sftp.put("scratch/check_aghu.py", "/var/app/sistemalec/scratch/check_aghu.py")
sftp.close()

# Executa o script na VM com PYTHONPATH=.
stdin, stdout, stderr = ssh.exec_command("cd /var/app/sistemalec && PYTHONPATH=. /root/.local/bin/uv run python scratch/check_aghu.py")
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))
ssh.close()
