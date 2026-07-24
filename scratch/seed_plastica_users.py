import sqlite3
import os
import sys
import paramiko
from dotenv import load_dotenv

load_dotenv()

# Usuários a cadastrar
NOVOS_USUARIOS = [
    # Residentes da Plástica
    {"username": "matheus.belem", "nome": "Matheus Santana Belém", "funcao": "Residente", "especialidade": "Plástica", "perfil_id": "PLASTICA"},
    {"username": "leonaldo.diniz", "nome": "Leonaldo Torres Diniz", "funcao": "Residente", "especialidade": "Plástica", "perfil_id": "PLASTICA"},
    {"username": "ravelly.cunha", "nome": "Ravelly Mais Cunha", "funcao": "Residente", "especialidade": "Plástica", "perfil_id": "PLASTICA"},
    {"username": "andre.veleda", "nome": "André Matheus de Souza Veleda", "funcao": "Residente", "especialidade": "Plástica", "perfil_id": "PLASTICA"},
    {"username": "layane.duarte", "nome": "Layane Duarte Silva", "funcao": "Residente", "especialidade": "Plástica", "perfil_id": "PLASTICA"},
    {"username": "tarsis.costa", "nome": "Tarsis Zaire Ferreira da Costa", "funcao": "Residente", "especialidade": "Plástica", "perfil_id": "PLASTICA"},
    
    # Enfermeira da Plástica
    {"username": "karla.romana", "nome": "Karla Romana Ferreira de Souza", "funcao": "Enfermeiro", "especialidade": "Plástica", "perfil_id": "PLASTICA"},
]

def seed_db(db_path):
    print(f"\n--- Cadastrando usuários em: {db_path} ---")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verificar se perfil PLASTICA existe
    cursor.execute("SELECT id FROM perfis WHERE id = 'PLASTICA'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO perfis (id, nome, tipo, cor, especialidade) VALUES ('PLASTICA', 'PLÁSTICA', 'ESPECIALIDADE', 'verde', 'Plástica')")
        print("Perfil PLÁSTICA inserido.")

    added = 0
    updated = 0

    for u in NOVOS_USUARIOS:
        cursor.execute("SELECT id FROM usuarios WHERE LOWER(username) = LOWER(?)", (u['username'],))
        row = cursor.fetchone()
        if row:
            cursor.execute("""
                UPDATE usuarios 
                SET nome = ?, funcao = ?, especialidade = ?, perfil_id = ?
                WHERE id = ?
            """, (u['nome'], u['funcao'], u['especialidade'], u['perfil_id'], row[0]))
            updated += 1
            print(f"  [ATUALIZADO] {u['nome']} ({u['username']}) -> {u['funcao']}")
        else:
            cursor.execute("""
                INSERT INTO usuarios (username, nome, perfil_id, especialidade, funcao)
                VALUES (?, ?, ?, ?, ?)
            """, (u['username'], u['nome'], u['perfil_id'], u['especialidade'], u['funcao']))
            added += 1
            print(f"  [INSERIDO] {u['nome']} ({u['username']}) -> {u['funcao']}")

    conn.commit()
    conn.close()
    print(f"Concluído: {added} inseridos, {updated} atualizados.")

def main():
    # 1. Atualiza local
    local_db = "data/app.db"
    if os.path.exists(local_db):
        seed_db(local_db)
    else:
        print(f"Banco local {local_db} não encontrado!")

    # 2. Upload/Atualiza na VM via SSH/SCP
    host = os.getenv("LEC_VM_HOST")
    user = os.getenv("LEC_VM_USER")
    password = os.getenv("LEC_VM_PASSWORD")

    if host and user and password:
        print(f"\n--- Conectando à VM {host} para atualizar banco remoto ---")
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, username=user, password=password)

            # Envia o banco local atualizado para a VM
            sftp = ssh.open_sftp()
            remote_path = "/var/app/sistemalec/data/app.db"
            print(f"Enviando {local_db} para VM em {remote_path}...")
            sftp.put(local_db, remote_path)
            sftp.close()

            # Reinicia o serviço na VM para garantir recarga
            stdin, stdout, stderr = ssh.exec_command("systemctl restart sistemalec")
            print("Serviço sistemalec reiniciado na VM.")
            ssh.close()
            print("\n==================================================")
            print("Sucesso! Usuários inseridos no banco local e na VM!")
            print("==================================================")
        except Exception as e:
            print(f"Erro ao atualizar na VM: {e}")

if __name__ == "__main__":
    main()
