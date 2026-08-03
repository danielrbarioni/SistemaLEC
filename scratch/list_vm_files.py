import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

stdin, stdout, stderr = ssh.exec_command("find /var/app/sistemalec/ -type f 2>/dev/null")
print("Arquivos no projeto na VM:\n", stdout.read().decode())

ssh.close()
