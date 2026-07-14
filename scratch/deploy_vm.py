import os
import sys

# Tenta carregar o python-dotenv se estiver disponível
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback simples caso python-dotenv não esteja instalado
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")

import paramiko

# Lê as configurações do arquivo .env
hostname = os.getenv("LEC_VM_HOST")
username = os.getenv("LEC_VM_USER")
password = os.getenv("LEC_VM_PASSWORD")

if not hostname or not username or not password:
    print("Erro: As variáveis LEC_VM_HOST, LEC_VM_USER e LEC_VM_PASSWORD devem estar definidas no arquivo .env!")
    sys.exit(1)

# Lista de comandos que serão executados na VM sequencialmente
commands = [
    # 1. Instalar utilitários essenciais
    "apt update && apt install -y git curl ufw systemd openssh-server python3",
    # 2. Instalar Podman & Podman-Compose
    "apt install -y podman podman-compose",
    # 3. Criar diretório de destino da aplicação
    "mkdir -p /var/app/sistemalec",
    "chown -R $USER:$USER /var/app/sistemalec",
    # 4. Criar pasta de dados persistentes do SQLite
    "mkdir -p /var/app/sistemalec/data"
]

def run_remote_commands():
    print(f"Conectando ao host {hostname} como {username}...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=15)
        print("Conectado com sucesso!\n")
        
        for cmd in commands:
            print(f"Executando: {cmd}")
            # Usamos get_pty=True para comandos que usam sudo para podermos fornecer a senha se necessário
            stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
            
            # Envia a senha para o prompt do sudo se solicitado
            stdin.write(password + "\n")
            stdin.flush()
            
            # Lê a saída em tempo real
            for line in stdout:
                try:
                    print(f"  [OUT] {line.strip()}")
                except UnicodeEncodeError:
                    safe_line = line.strip().encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8', errors='replace')
                    print(f"  [OUT] {safe_line}")
            for line in stderr:
                try:
                    print(f"  [ERR] {line.strip()}")
                except UnicodeEncodeError:
                    safe_line = line.strip().encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8', errors='replace')
                    print(f"  [ERR] {safe_line}")
                
            print("-" * 50)
            
        print("\nConfiguração concluída com sucesso na VM!")
        
    except Exception as e:
        print(f"\nErro durante a execução: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    run_remote_commands()
