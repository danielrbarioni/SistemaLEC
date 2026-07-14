import os
import sys
import paramiko

# Carrega as configurações do .env local
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

# Configuração simples de Proxy Reverso no Nginx
nginx_conf = """server {
    listen 80;
    server_name _;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""

def execute_remote_cmd(ssh, cmd):
    print(f"\n[CMD] {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    stdin.write(password + "\n")
    stdin.flush()
    
    for line in stdout:
        try:
            print(line.strip())
        except UnicodeEncodeError:
            safe_line = line.strip().encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8', errors='replace')
            print(safe_line)

def setup_nginx():
    print(f"Conectando ao host {hostname} para configurar o Nginx...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=15)
        print("Conectado com sucesso!")
        
        # 1. Instalar Nginx
        print("\nInstalando Nginx na VM...")
        execute_remote_cmd(ssh, "apt-get update && apt-get install -y nginx")
        
        # 2. Upload da configuração
        print("\nConfigurando proxy reverso no Nginx...")
        sftp = ssh.open_sftp()
        with sftp.open("/etc/nginx/sites-available/sistemalec", "w") as f:
            f.write(nginx_conf)
        sftp.close()
        
        # 3. Habilitar a nova configuração e desabilitar a padrão
        execute_remote_cmd(ssh, "ln -sf /etc/nginx/sites-available/sistemalec /etc/nginx/sites-enabled/sistemalec")
        execute_remote_cmd(ssh, "rm -f /etc/nginx/sites-enabled/default")
        
        # 4. Validar e reiniciar o Nginx
        execute_remote_cmd(ssh, "nginx -t")
        execute_remote_cmd(ssh, "systemctl restart nginx")
        execute_remote_cmd(ssh, "systemctl enable nginx")
        
        print("\n==================================================")
        print("Nginx configurado com sucesso!")
        print(f"Agora voce pode acessar a aplicacao direto no IP: http://{hostname}")
        print("==================================================")
        
    except Exception as e:
        print(f"\nErro ao configurar Nginx: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    setup_nginx()
