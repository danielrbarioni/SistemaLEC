import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

# Para o serviço brevemente para fazer a exclusão limpa
stdin, stdout, stderr = ssh.exec_command("systemctl stop sistemalec")
stdout.read()

stdin, stdout, stderr = ssh.exec_command("""python3 -c "
import sqlite3
db_path = '/var/app/sistemalec/data/app.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('''
    DELETE FROM solicitacoes 
    WHERE data_criacao LIKE '%2026-07-31%' 
       OR data_criacao LIKE '%31/07/2026%'
       OR id = '2ff11436'
''')
count = c.rowcount
conn.commit()

c.execute(\\\"SELECT COUNT(*) FROM solicitacoes WHERE data_criacao LIKE '%2026-07-31%'\\\")
rem = c.fetchone()[0]
print(f'Solicitações deletadas: {count}. Restantes do dia 31/07/2026: {rem}')

conn.close()
" """)

print(stdout.read().decode('utf-8', errors='replace'))

# Inicia o serviço novamente
stdin, stdout, stderr = ssh.exec_command("systemctl start sistemalec")
stdout.read()

ssh.close()
