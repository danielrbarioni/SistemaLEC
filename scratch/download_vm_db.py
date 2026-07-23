import os
import paramiko
from dotenv import load_dotenv

load_dotenv()

HOSTNAME = os.getenv("LEC_VM_HOST", "10.34.0.202")
USERNAME = os.getenv("LEC_VM_USER", "root")
PASSWORD = os.getenv("LEC_VM_PASSWORD")

def download_db():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    
    sftp = ssh.open_sftp()
    remote_path = '/var/app/sistemalec/data/app.db'
    local_path = 'data/app.db'
    
    print(f"Baixando banco de dados real da VM ({remote_path}) para ({local_path})...")
    sftp.get(remote_path, local_path)
    sftp.close()
    ssh.close()
    print("Banco de dados sincronizado com sucesso da VM!")

if __name__ == "__main__":
    download_db()
