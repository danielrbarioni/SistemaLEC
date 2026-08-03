import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

stdin, stdout, stderr = ssh.exec_command("""python3 -c "
import sqlite3
db_path = '/var/app/sistemalec/data/app.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Buscar solicitacoes onde a data contenha 24/07/2026, 2026-07-24, ou referente ao paciente ADRIANA
cursor.execute('''
    SELECT id, tipo, data_criacao, codigo_paciente, nome_paciente, detalhes 
    FROM solicitacoes 
    WHERE data_criacao LIKE '%24/07/2026%' 
       OR data_criacao LIKE '%2026-07-24%'
       OR data_criacao LIKE '%24-07-2026%'
       OR nome_paciente LIKE '%ADRIANA CRISTINA BARBOSA DE LIMA%'
''')
solics = cursor.fetchall()
print(f'Solicitações encontradas: {len(solics)}')
for s in solics:
    print(' ', s)

conn.close()
" """)

print("Output:\n", stdout.read().decode('utf-8', errors='replace'))
ssh.close()
