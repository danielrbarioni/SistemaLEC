import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

script_content = """#!/bin/bash
BACKUP_DIR="/var/backups/sistemalec"
DB_PATH="/var/lib/sistemalec/app.db"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

if [ -f "$DB_PATH" ]; then
    if command -v sqlite3 >/dev/null 2>&1; then
        sqlite3 "$DB_PATH" ".backup '$BACKUP_DIR/app_$DATE.db'"
    else
        cp "$DB_PATH" "$BACKUP_DIR/app_$DATE.db"
    fi
    find "$BACKUP_DIR" -name "app_*.db" -mtime +30 -delete
fi
"""

# Open SFTP and write script directly
sftp = ssh.open_sftp()
with sftp.file('/var/lib/sistemalec/backup_db.sh', 'w') as f:
    f.write(script_content)
sftp.close()

# Make executable and run
ssh.exec_command('chmod +x /var/lib/sistemalec/backup_db.sh')
ssh.exec_command('/var/lib/sistemalec/backup_db.sh')

# Verify backup files
_, stdout, _ = ssh.exec_command('ls -la /var/backups/sistemalec/')
print("=== ARQUIVOS DE BACKUP NA VM: ===")
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
