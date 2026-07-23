import os
import paramiko
from dotenv import load_dotenv

load_dotenv()

HOSTNAME = os.getenv("LEC_VM_HOST", "10.34.0.202")
USERNAME = os.getenv("LEC_VM_USER", "root")
PASSWORD = os.getenv("LEC_VM_PASSWORD")

def fix_vm():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    
    print("1. Enviando app.db local atualizado com historico para a VM...")
    sftp = ssh.open_sftp()
    local_db = 'data/app.db'
    remote_db = '/var/app/sistemalec/data/app.db'
    sftp.put(local_db, remote_db)
    sftp.close()
    print("app.db enviado com sucesso para a VM!")
    
    print("2. Aplicando migracao alembic na VM...")
    stdin, stdout, stderr = ssh.exec_command('cd /var/app/sistemalec && /root/.local/bin/uv run alembic upgrade head')
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    print("3. Reiniciando o servico sistemalec na VM...")
    stdin, stdout, stderr = ssh.exec_command('systemctl restart sistemalec')
    print(stdout.read().decode())
    
    ssh.close()
    print("Correcao concluida na VM!")

if __name__ == "__main__":
    fix_vm()
