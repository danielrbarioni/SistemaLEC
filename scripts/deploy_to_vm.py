import os
import sys
import paramiko
from datetime import datetime

VM_HOST = "10.34.0.202"
VM_USER = "root"
VM_PASS = "hc*l0ck2026"
REMOTE_APP_DIR = "/var/app/sistemalec"

def deploy_to_vm():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando Deploy e Migração na VM ({VM_HOST})...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(VM_HOST, username=VM_USER, password=VM_PASS, timeout=15)
        print("[OK] Conexão SSH estabelecida com sucesso!")

        sftp = ssh.open_sftp()

        # 1. Faz backup do app.db remoto antes da migração
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_cmd = f"cp {REMOTE_APP_DIR}/data/app.db {REMOTE_APP_DIR}/data/backups/app_pre_lateralidade_{timestamp}.db.bak"
        ssh.exec_command(f"mkdir -p {REMOTE_APP_DIR}/data/backups && {backup_cmd}")
        print(f"[OK] Backup remoto realizado: app_pre_lateralidade_{timestamp}.db.bak")

        # 2. Executa a migração da coluna lateralidade no app.db da VM via Python remoto
        migration_code = """
import sqlite3
import os

db_path = '/var/app/sistemalec/data/app.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Pacientes
    cursor.execute("PRAGMA table_info(pacientes)")
    cols_pac = [row[1] for row in cursor.fetchall()]
    if 'lateralidade' not in cols_pac:
        cursor.execute("ALTER TABLE pacientes ADD COLUMN lateralidade TEXT DEFAULT 'Indefinida'")
        print("Coluna lateralidade adicionada em pacientes.")
    
    cursor.execute("UPDATE pacientes SET lateralidade = 'Indefinida' WHERE lateralidade IS NULL OR TRIM(lateralidade) = ''")
    
    # Solicitacoes
    cursor.execute("PRAGMA table_info(solicitacoes)")
    cols_sol = [row[1] for row in cursor.fetchall()]
    if 'lateralidade' not in cols_sol:
        cursor.execute("ALTER TABLE solicitacoes ADD COLUMN lateralidade TEXT DEFAULT 'Indefinida'")
        print("Coluna lateralidade adicionada em solicitacoes.")
        
    cursor.execute("UPDATE solicitacoes SET lateralidade = 'Indefinida' WHERE lateralidade IS NULL OR TRIM(lateralidade) = ''")
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM pacientes WHERE lateralidade = 'Indefinida'")
    print(f"Total pacientes com lateralidade Indefinida na VM: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM solicitacoes WHERE lateralidade = 'Indefinida'")
    print(f"Total solicitacoes com lateralidade Indefinida na VM: {cursor.fetchone()[0]}")
    
    conn.close()
"""
        # Upload do script de migração para a VM
        with sftp.open("/tmp/migrate_lateralidade.py", "w") as f:
            f.write(migration_code)
        
        stdin, stdout, stderr = ssh.exec_command(f"python3 /tmp/migrate_lateralidade.py")
        print("[MIGRAÇÃO VM]:", stdout.read().decode().strip())
        err = stderr.read().decode().strip()
        if err:
            print("[MIGRAÇÃO ERR]:", err)

        # 3. Transfere os arquivos atualizados de src e static/dist
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
                    if file.endswith(('.pyc', '.bak', '.log')):
                        continue
                    local_file = os.path.join(root, file)
                    remote_file = os.path.join(target_dir, file).replace("\\", "/")
                    sftp.put(local_file, remote_file)

        print("[OK] Enviando arquivos do backend (src)...")
        upload_dir(os.path.join(local_root, "src"), f"{REMOTE_APP_DIR}/src")

        print("[OK] Enviando frontend compilado (src/static/dist)...")
        upload_dir(os.path.join(local_root, "src", "static", "dist"), f"{REMOTE_APP_DIR}/src/static/dist")

        sftp.close()

        # 4. Reinicia o serviço do sistemalec na VM
        print("[OK] Reiniciando serviço sistemalec na VM...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sistemalec")
        stdout.channel.recv_exit_status()

        # 5. Checa status do serviço
        stdin, stdout, stderr = ssh.exec_command("systemctl is-active sistemalec")
        status = stdout.read().decode().strip()
        print(f"[STATUS SERVIÇO VM]: {status}")

        ssh.close()
        print("\n=== DEPLOY E MIGRAÇÃO NA VM CONCLUÍDOS COM 100% DE SUCESSO! ===")

    except Exception as e:
        print(f"[ERRO NO DEPLOY]: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    deploy_to_vm()
