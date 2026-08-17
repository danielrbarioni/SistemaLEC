import os
import sys
import shutil
from datetime import datetime
import paramiko

VM_HOST = "10.34.0.202"
VM_USER = "root"
VM_PASS = "hc*l0ck2026"
REMOTE_DB_PATH = "/var/app/sistemalec/data/app.db"
LOCAL_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "app.db"))
BACKUP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "backups"))

def sync_db_from_vm():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando sincronizacao VM -> Local...")
    
    # 1. Garante diretorio de backups
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # 2. Se o banco local existir, cria backup com timestamp
    if os.path.exists(LOCAL_DB_PATH):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"app_local_{timestamp}.db.bak")
        shutil.copy2(LOCAL_DB_PATH, backup_file)
        print(f"[OK] Backup do banco local salvo em: {backup_file}")

    # 3. Conexao SSH / SFTP com a VM
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(VM_HOST, username=VM_USER, password=VM_PASS, timeout=15)
        sftp = ssh.open_sftp()
        
        # Puxa o banco da VM
        sftp.get(REMOTE_DB_PATH, LOCAL_DB_PATH)
        sftp.close()
        ssh.close()
        
        tamanho_kb = os.path.getsize(LOCAL_DB_PATH) / 1024
        print(f"[OK] Banco de dados sincronizado com sucesso da VM ({tamanho_kb:.1f} KB).")
        print("[OK] Ambiente local agora possui 100% dos dados reais da VM!")
    except Exception as e:
        print(f"[ERRO] Erro ao sincronizar banco da VM: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    sync_db_from_vm()
