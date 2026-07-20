import os
import sys
import paramiko

# Carrega configurações do .env local
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")

hostname = os.getenv("LEC_VM_HOST")
username = os.getenv("LEC_VM_USER")
password = os.getenv("LEC_VM_PASSWORD")

if not hostname or not username or not password:
    print("Erro: As variaveis LEC_VM_HOST, LEC_VM_USER e LEC_VM_PASSWORD devem estar definidas no arquivo .env!")
    sys.exit(1)

def execute_remote_cmd(ssh, cmd):
    print(f"\n--- [CMD] {cmd} ---")
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    stdin.write(password + "\n")
    stdin.flush()
    
    for line in stdout:
        try:
            print(line.strip())
        except UnicodeEncodeError:
            safe_line = line.strip().encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8', errors='replace')
            print(safe_line)

def restart_service():
    print(f"Conectando a VM {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=15)
        print("Conectado! Reiniciando o servico sistemalec na VM...")
        
        # Reiniciar o serviço sistemalec
        execute_remote_cmd(ssh, "systemctl restart sistemalec")
        
        # Verificar o status após o reinício
        execute_remote_cmd(ssh, "systemctl status sistemalec --no-pager")
        
    except Exception as e:
        print(f"Erro ao reiniciar o servico na VM: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    restart_service()
