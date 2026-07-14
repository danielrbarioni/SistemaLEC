import os
import sys
import paramiko
from dotenv import load_dotenv

load_dotenv()

hostname = os.getenv("LEC_VM_HOST")
username = os.getenv("LEC_VM_USER")
password = os.getenv("LEC_VM_PASSWORD")

if not hostname or not username or not password:
    print("Erro: As variáveis LEC_VM_HOST, LEC_VM_USER e LEC_VM_PASSWORD devem estar definidas no arquivo .env!")
    sys.exit(1)

def execute_remote_cmd(ssh, cmd):
    print(f"\nExecutando: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    stdin.write(password + "\n")
    stdin.flush()
    for line in stdout:
        print(f"  [OUT] {line.strip()}")
    for line in stderr:
        print(f"  [ERR] {line.strip()}")

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Conectando ao servidor remoto {hostname}...")
    ssh.connect(hostname, username=username, password=password)

    try:
        sftp = ssh.open_sftp()
        print("Enviando script de limpeza para o servidor remoto...")
        sftp.put("scratch/clear_db.py", "/var/app/sistemalec/scratch/clear_db.py")
        sftp.close()

        # Executa o script de limpeza na VM usando o ambiente do uv
        execute_remote_cmd(ssh, "cd /var/app/sistemalec && /root/.local/bin/uv run python scratch/clear_db.py")

        # Limpa o script da VM
        execute_remote_cmd(ssh, "rm -f /var/app/sistemalec/scratch/clear_db.py")

        # Reinicia o serviço FastAPI para garantir que as conexões ativas limpem o cache em memória se houver
        execute_remote_cmd(ssh, "systemctl restart sistemalec")
        print("\nBanco de dados remoto limpo e serviço sistemalec reiniciado!")

    finally:
        ssh.close()

if __name__ == "__main__":
    main()
