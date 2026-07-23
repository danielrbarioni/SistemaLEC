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
    print("Erro: As variáveis LEC_VM_HOST, LEC_VM_USER e LEC_VM_PASSWORD devem estar definidas no arquivo .env!")
    sys.exit(1)

# Definição do arquivo de serviço systemd
service_content = """[Unit]
Description=Sistema LEC FastAPI Backend
After=network.target

[Service]
User=root
WorkingDirectory=/var/app/sistemalec
EnvironmentFile=/var/app/sistemalec/.env
ExecStart=/root/.local/bin/uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
"""

def execute_remote_cmd(ssh, cmd):
    print(f"\nExecutando: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    stdin.write(password + "\n")
    stdin.flush()
    
    # Imprime saída em tempo real tratando codificação no console Windows
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

def deploy():
    print(f"Conectando ao host {hostname} como {username}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=15)
        print("Conectado com sucesso!")
        
        # 1. Copiar o arquivo .env local para a VM usando SFTP
        print("\nEnviando arquivo .env local para a VM...")
        sftp = ssh.open_sftp()
        sftp.put(".env", "/var/app/sistemalec/.env")
        sftp.close()
        print("Arquivo .env enviado com sucesso.")
        
        # 2. Corrigir repositório CD-ROM local se necessário e instalar dependências essenciais
        print("\nConfigurando pacotes e repositorios (desabilitando CD-ROM)...")
        execute_remote_cmd(ssh, "sed -i '/cdrom:/s/^/#/' /etc/apt/sources.list || true")
        execute_remote_cmd(ssh, "apt-get update && apt-get install -y git curl nodejs npm ufw systemd openssh-server python3 podman podman-compose")

        # 3. Inicializar o repositório Git e baixar o código (evita problemas se a pasta não estiver vazia)
        git_setup = (
            "cd /var/app/sistemalec && "
            "if [ ! -d .git ]; then "
            "  git init && "
            "  git remote add origin https://github.com/danielrbarioni/SistemaLEC.git && "
            "  git fetch && "
            "  git checkout -f main; "
            "else "
            "  git fetch --all && "
            "  git reset --hard origin/main; "
            "fi"
        )
        execute_remote_cmd(ssh, git_setup)

        # Criar os diretórios necessários na VM
        execute_remote_cmd(ssh, "mkdir -p /var/app/sistemalec/src/models /var/app/sistemalec/src/providers/implementations /var/app/sistemalec/src/providers/interfaces /var/app/sistemalec/scratch /var/app/sistemalec/src/auth /var/app/sistemalec/src/providers/sql/paciente")

        # Copiar todos os arquivos novos e modificados para a VM
        print("\nEnviando arquivos novos e modificados localmente para a VM...")
        sftp = ssh.open_sftp()
        
        files_to_upload = [
            ("frontend/vite.config.ts", "/var/app/sistemalec/frontend/vite.config.ts"),
            ("frontend/src/views/InteracoesLec.vue", "/var/app/sistemalec/frontend/src/views/InteracoesLec.vue"),
            ("frontend/src/views/Pacientes.vue", "/var/app/sistemalec/frontend/src/views/Pacientes.vue"),
            ("src/main.py", "/var/app/sistemalec/src/main.py"),
            ("src/dependencies.py", "/var/app/sistemalec/src/dependencies.py"),
            ("src/auth/auth.py", "/var/app/sistemalec/src/auth/auth.py"),
            ("src/models/paciente.py", "/var/app/sistemalec/src/models/paciente.py"),
            ("src/models/solicitacao.py", "/var/app/sistemalec/src/models/solicitacao.py"),
            ("src/models/status_local.py", "/var/app/sistemalec/src/models/status_local.py"),
            ("src/providers/implementations/paciente_sqlite_provider.py", "/var/app/sistemalec/src/providers/implementations/paciente_sqlite_provider.py"),
            ("src/providers/implementations/paciente_hybrid_provider.py", "/var/app/sistemalec/src/providers/implementations/paciente_hybrid_provider.py"),
            ("src/providers/implementations/solicitacao_sqlite_provider.py", "/var/app/sistemalec/src/providers/implementations/solicitacao_sqlite_provider.py"),
            ("src/routers/paciente.py", "/var/app/sistemalec/src/routers/paciente.py"),
            ("src/routers/solicitacao.py", "/var/app/sistemalec/src/routers/solicitacao.py"),
            ("src/providers/interfaces/paciente_provider_interface.py", "/var/app/sistemalec/src/providers/interfaces/paciente_provider_interface.py"),
            ("src/providers/implementations/paciente_postgres_provider.py", "/var/app/sistemalec/src/providers/implementations/paciente_postgres_provider.py"),
            ("src/providers/sql/paciente/listar_pacientes.sql", "/var/app/sistemalec/src/providers/sql/paciente/listar_pacientes.sql"),
            ("src/providers/sql/paciente/obter_paciente.sql", "/var/app/sistemalec/src/providers/sql/paciente/obter_paciente.sql"),
            ("src/providers/sql/paciente/procedimentos_especialidade.sql", "/var/app/sistemalec/src/providers/sql/paciente/procedimentos_especialidade.sql"),
            ("frontend/index.html", "/var/app/sistemalec/frontend/index.html"),
            ("frontend/src/layouts/DefaultLayout.vue", "/var/app/sistemalec/frontend/src/layouts/DefaultLayout.vue"),
            ("frontend/src/router/index.ts", "/var/app/sistemalec/frontend/src/router/index.ts"),
            ("scratch/migrate_csv_to_sqlite.py", "/var/app/sistemalec/scratch/migrate_csv_to_sqlite.py")
        ]
        
        for local_file, remote_file in files_to_upload:
            if os.path.exists(local_file):
                print(f"  -> Enviando {local_file}...")
                sftp.put(local_file, remote_file)
            else:
                print(f"  -> Aviso: Arquivo {local_file} não encontrado localmente.")
        sftp.close()
        print("Arquivos locais enviados com sucesso.")
        
        # 4. Instalar uv (se não existir)
        print("\nInstalando uv...")
        execute_remote_cmd(ssh, "curl -LsSf https://astral.sh/uv/install.sh | sh")
        
        # 5. Instalar dependências e gerar build do frontend
        print("\nSincronizando dependencias Python (uv)...")
        execute_remote_cmd(ssh, "cd /var/app/sistemalec && /root/.local/bin/uv sync")

        print("\nExecutando migrações Alembic na VM...")
        execute_remote_cmd(ssh, "cd /var/app/sistemalec && /root/.local/bin/uv run alembic upgrade head")
        
        print("\nInstalando dependencias do frontend e gerando build...")
        execute_remote_cmd(ssh, "cd /var/app/sistemalec/frontend && npm install && npm run build")
        
        # 6. Criar e configurar o serviço systemd para iniciar a aplicação automaticamente
        print("\nConfigurando servico systemd...")
        # Escreve o arquivo de serviço na VM
        sftp = ssh.open_sftp()
        with sftp.open("/etc/systemd/system/sistemalec.service", "w") as f:
            f.write(service_content)
        sftp.close()
        
        # Habilitar e iniciar o serviço
        execute_remote_cmd(ssh, "systemctl daemon-reload")
        execute_remote_cmd(ssh, "systemctl enable sistemalec")
        execute_remote_cmd(ssh, "systemctl restart sistemalec")
        
        print("\n==================================================")
        print("Deploy concluido com sucesso!")
        print(f"A aplicacao esta rodando em background na VM!")
        print("==================================================")
        
    except Exception as e:
        print(f"\nErro durante o deploy: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy()
