import paramiko

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)
    print("Conexão SSH estabelecida com sucesso!")
    
    stdin, stdout, stderr = ssh.exec_command("find / -name app.db 2>/dev/null")
    db_paths = stdout.read().decode().strip().split('\n')
    print("Caminhos do app.db encontrados na VM:", db_paths)
    
    if db_paths and db_paths[0]:
        remote_path = db_paths[0]
        sftp = ssh.open_sftp()
        local_path = r"c:\Users\daniel.barioni\.gemini\antigravity-ide\scratch\Antigravity IDE\Sistema LEC\data\app.db"
        sftp.get(remote_path, local_path)
        sftp.close()
        print(f"Banco de dados copiado com sucesso de {remote_path} para {local_path}!")
    else:
        print("Arquivo app.db não localizado na VM.")
    ssh.close()
except Exception as e:
    print(f"Erro ao conectar via SSH/SFTP: {e}")
