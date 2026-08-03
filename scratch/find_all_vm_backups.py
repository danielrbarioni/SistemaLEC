import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

cmd = 'find /var/app /root /tmp -name "*.db*" 2>/dev/null'
stdin, stdout, stderr = ssh.exec_command(cmd)
files = [f.strip() for f in stdout.read().decode().splitlines() if f.strip()]

print("Arquivos DB encontrados na VM:")
for f in files:
    print(" ->", f)
    cmd_py = f"""python3 -c "import sqlite3; conn=sqlite3.connect('{f}'); print(conn.execute('SELECT name FROM sqlite_master WHERE type=\\'table\\'').fetchall())" """
    _, stdout2, stderr2 = ssh.exec_command(cmd_py)
    print("    Tables:", stdout2.read().decode().strip(), stderr2.read().decode().strip())

ssh.close()
