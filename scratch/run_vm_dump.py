import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

stdin, stdout, stderr = ssh.exec_command("python3 /var/app/sistemalec/scratch/dump_db_content.py")
print("Output do dump na VM:\n", stdout.read().decode())
print("Errors:\n", stderr.read().decode())

ssh.close()
