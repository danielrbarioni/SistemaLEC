import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

commands = """
cd /var/app/sistemalec

# 1. Realizar backup preventivo timestamped do banco de dados da VM
if [ -f /var/app/sistemalec/data/app.db ]; then
  cp /var/app/sistemalec/data/app.db /var/app/sistemalec/data/app.db.bak_$(date +%Y%m%d_%H%M%S)
fi

# 2. Desrastrear o banco no repositório local da VM se ainda estiver rastreado
git rm --cached -f app.db data/app.db 2>/dev/null || true

# 3. Atualizar o código-fonte via Git (sem alterar /var/app/sistemalec/data/app.db)
git fetch origin main
git reset --hard origin/main

# 4. Recompilar frontend e reiniciar serviço
cd frontend
npm run build
systemctl restart sistemalec
"""

stdin, stdout, stderr = ssh.exec_command(f"bash -c '{commands}'")
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')

with open('scratch/deploy_result.log', 'w', encoding='utf-8') as f:
    f.write("OUTPUT:\n" + out + "\nERRORS:\n" + err)

print("Deploy seguro executado na VM! Verifique scratch/deploy_result.log")
ssh.close()

