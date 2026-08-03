import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=15)

# Step 1: Stop service and prepare directory
ssh.exec_command("systemctl stop sistemalec || true")
ssh.exec_command("mkdir -p /var/lib/sistemalec /var/backups/sistemalec")

# Step 2: Copy DB
ssh.exec_command("cp -f /var/app/sistemalec/data/app.db /var/lib/sistemalec/app.db")

# Step 3: Verify DB in /var/lib/sistemalec/app.db
verify_cmd = """python3 -c "
import sqlite3
conn = sqlite3.connect('/var/lib/sistemalec/app.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM usuarios')
u_cnt = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM solicitacoes')
s_cnt = c.fetchone()[0]
print(f'=== SUCESSO: BANCO ISOLADO EM /var/lib/sistemalec/app.db POSSUI {u_cnt} USUÁRIOS E {s_cnt} SOLICITAÇÕES. ===')
conn.close()
" """
stdin, stdout, stderr = ssh.exec_command(verify_cmd)
print(stdout.read().decode('utf-8', errors='replace'))

# Step 4: Update .env in VM
update_env_cmd = """
sed -i 's|APP_DB_URL=.*|APP_DB_URL=sqlite+aiosqlite:////var/lib/sistemalec/app.db|g' /var/app/sistemalec/.env
sed -i 's|SQLITE_DSN=.*|SQLITE_DSN=sqlite+aiosqlite:////var/lib/sistemalec/app.db|g' /var/app/sistemalec/.env
"""
ssh.exec_command(f"bash -c '{update_env_cmd}'")

# Step 5: Create backup script
backup_script = """cat << 'EOF' > /var/lib/sistemalec/backup_db.sh
#!/bin/bash
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
EOF
chmod +x /var/lib/sistemalec/backup_db.sh
"""
ssh.exec_command(f"bash -c '{backup_script}'")

# Step 6: Execute first backup and set crontab
ssh.exec_command("/var/lib/sistemalec/backup_db.sh")
ssh.exec_command('bash -c "(crontab -l 2>/dev/null | grep -v \'/var/lib/sistemalec/backup_db.sh\' ; echo \'0 1 * * * /var/lib/sistemalec/backup_db.sh\') | crontab -"')

# Step 7: Restart service
ssh.exec_command("systemctl start sistemalec")

# Step 8: Verify backups created
stdin, stdout, stderr = ssh.exec_command("ls -la /var/backups/sistemalec/")
print("=== BACKUPS CRIADOS NA VM: ===")
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
print("Blindagem concluída com sucesso!")

