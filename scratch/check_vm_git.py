import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

stdin, stdout, stderr = ssh.exec_command("cd /var/app/sistemalec && git log -n 1 --oneline && git status -s")
print("Status do Git na VM:\n", stdout.read().decode('utf-8', errors='replace'))
ssh.close()
