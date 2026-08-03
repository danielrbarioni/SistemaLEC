import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.34.0.202', username='root', password='hc*l0ck2026', timeout=10)

stdin, stdout, stderr = ssh.exec_command("""python3 -c "
import sqlite3
db_path = '/var/app/sistemalec/data/app.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Excluir explicitamente os IDs das solicitacoes e respostas do dia 24/07/2026
cursor.execute(\\\"DELETE FROM solicitacoes WHERE id IN ('c9fc59fd', '4d482c98') OR data_criacao LIKE '%2026-07-24%' OR data_criacao LIKE '%24/07/2026%'\\\")
count = cursor.rowcount
conn.commit()
print(f'Solicitações deletadas no banco /var/app/sistemalec/data/app.db: {count}')

# Garantir que o perfil OBSERVADOR esta inserido
cursor.execute(\\\"INSERT OR REPLACE INTO perfis (id, nome, tipo, cor, especialidade) VALUES ('OBSERVADOR', 'OBSERVADOR', 'OBSERVADOR', 'cinza', NULL)\\\")
conn.commit()

# Conferir perfis atuais no banco da VM
cursor.execute('SELECT id, nome, tipo, especialidade FROM perfis')
print('Perfis no banco da VM:', cursor.fetchall())

conn.close()
" """)

print("Output da exclusao e conferencia:\n", stdout.read().decode('utf-8', errors='replace'))
ssh.close()
