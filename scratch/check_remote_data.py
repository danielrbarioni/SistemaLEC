import os
import paramiko
from dotenv import load_dotenv

load_dotenv()

HOSTNAME = os.getenv("LEC_VM_HOST", "10.34.0.202")
USERNAME = os.getenv("LEC_VM_USER", "root")
PASSWORD = os.getenv("LEC_VM_PASSWORD")

def check_remote():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    
    stdin, stdout, stderr = ssh.exec_command('ls -la /var/app/sistemalec/data/')
    print("--- Conteudo da pasta /var/app/sistemalec/data/ na VM ---")
    print(stdout.read().decode())
    
    stdin, stdout, stderr = ssh.exec_command('. /var/app/sistemalec/.venv/bin/activate && python3 -c "import sqlite3; conn = sqlite3.connect(\'/var/app/sistemalec/data/app.db\'); print([(t[0], conn.execute(f\'SELECT count(*) FROM {t[0]}\').fetchone()[0]) for t in conn.execute(\"SELECT name FROM sqlite_master WHERE type=\'table\'\").fetchall() if not t[0].startswith(\'sqlite\')])"')
    print("--- Registros no app.db da VM ---")
    print(stdout.read().decode())
    ssh.close()

if __name__ == "__main__":
    check_remote()
