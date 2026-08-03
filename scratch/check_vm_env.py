import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

stdin, stdout, stderr = ssh.exec_command("cat /var/app/sistemalec/.env")
print("Conteúdo do .env da VM:\n", stdout.read().decode())

ssh.close()
