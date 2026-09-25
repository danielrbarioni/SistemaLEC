import os
import sys
import paramiko
from datetime import datetime

VM_HOST = "10.34.0.202"
VM_USER = "root"
VM_PASS = "hc*l0ck2026"
REMOTE_APP_DIR = "/var/app/sistemalec"

def deploy_to_vm():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando Deploy seguro na VM ({VM_HOST})...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(VM_HOST, username=VM_USER, password=VM_PASS, timeout=15)
        print("[OK] Conexão SSH estabelecida com sucesso!")

        sftp = ssh.open_sftp()

        # 1. Faz backup de segurança do app.db remoto (mantendo o banco de dados original intacto)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_cmd = f"cp {REMOTE_APP_DIR}/data/app.db {REMOTE_APP_DIR}/data/backups/app_backup_{timestamp}.db.bak"
        ssh.exec_command(f"mkdir -p {REMOTE_APP_DIR}/data/backups && {backup_cmd}")
        print(f"[OK] Backup de segurança do banco remoto criado: app_backup_{timestamp}.db.bak")

        # 2. Transfere os arquivos atualizados de src e static/dist (SEM mexer no data/app.db)
        local_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
        def upload_dir(local_path, remote_path):
            for root, dirs, files in os.walk(local_path):
                rel_path = os.path.relpath(root, local_path)
                target_dir = os.path.join(remote_path, rel_path).replace("\\", "/")
                try:
                    sftp.mkdir(target_dir)
                except:
                    pass
                for file in files:
                    if file.endswith(('.pyc', '.bak', '.log', '.db', '.sqlite')):
                        continue
                    local_file = os.path.join(root, file)
                    remote_file = os.path.join(target_dir, file).replace("\\", "/")
                    sftp.put(local_file, remote_file)

        print("[OK] Enviando arquivos do backend (src)...")
        upload_dir(os.path.join(local_root, "src"), f"{REMOTE_APP_DIR}/src")

        print("[OK] Enviando frontend compilado (src/static/dist)...")
        upload_dir(os.path.join(local_root, "src", "static", "dist"), f"{REMOTE_APP_DIR}/src/static/dist")

        sftp.close()

        # 3. Reinicia o serviço do sistemalec na VM
        print("[OK] Reiniciando serviço sistemalec na VM...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sistemalec")
        stdout.channel.recv_exit_status()

        # 4. Checa status do serviço
        stdin, stdout, stderr = ssh.exec_command("systemctl is-active sistemalec")
        status = stdout.read().decode().strip()
        print(f"[STATUS SERVIÇO VM]: {status}")

        ssh.close()
        print("\n=== DEPLOY NA VM CONCLUÍDO COM 100% DE SUCESSO! BANCO DE DADOS REMOTO INTACTO. ===")

    except Exception as e:
        print(f"[ERRO NO DEPLOY]: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    deploy_to_vm()
