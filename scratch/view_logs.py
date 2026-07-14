import paramiko
import os
from dotenv import load_dotenv

load_dotenv()

hostname = os.getenv("LEC_VM_HOST")
username = os.getenv("LEC_VM_USER")
password = os.getenv("LEC_VM_PASSWORD")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username=username, password=password)

stdin, stdout, stderr = ssh.exec_command('journalctl -u sistemalec -n 50 --no-pager')
print(stdout.read().decode('utf-8'))
ssh.close()
