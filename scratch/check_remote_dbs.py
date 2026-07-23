import os
import paramiko
from dotenv import load_dotenv

load_dotenv()

HOSTNAME = os.getenv("LEC_VM_HOST", "10.34.0.202")
USERNAME = os.getenv("LEC_VM_USER", "root")
PASSWORD = os.getenv("LEC_VM_PASSWORD")

def check_remote_detail():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    
    cmd = '''python3 -c "
import sqlite3
for dbname in ['app.db', 'app.db.bak']:
    try:
        conn = sqlite3.connect('/var/app/sistemalec/data/' + dbname)
        tables = [t[0] for t in conn.execute(\\\"SELECT name FROM sqlite_master WHERE type='table'\\\").fetchall()]
        print('=== ' + dbname + ' ===')
        for t in tables:
            if not t.startswith('sqlite'):
                cnt = conn.execute(f'SELECT count(*) FROM {t}').fetchone()[0]
                print(f' {t}: {cnt}')
    except Exception as e:
        print(e)
"'''
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode())
    print(stderr.read().decode())
    ssh.close()

if __name__ == "__main__":
    check_remote_detail()
