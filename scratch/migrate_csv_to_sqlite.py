import os
import csv
import sqlite3

DB_PATH = 'data/app.db'
CSV_PACIENTES = 'data/pacientes.csv'
CSV_SOLICITACOES = 'data/solicitacoes.csv'
CSV_STATUS_LOCAIS = 'data/status_locais.csv'

def migrate():
    print("Iniciando migração de CSV para SQLite...")
    
    # Garante que a pasta data exista
    os.makedirs('data', exist_ok=True)
    
    # Conecta no banco SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Criar tabela de pacientes se não existir
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pacientes (
        codigo INTEGER PRIMARY KEY,
        nome TEXT NOT NULL,
        dt_nascimento TEXT,
        cpf TEXT,
        sexo TEXT,
        cor TEXT,
        nome_mae TEXT,
        nome_pai TEXT,
        data_hora_inicio TEXT,
        status_consulta TEXT,
        especialidade TEXT,
        procedimento TEXT,
        ultima_consulta_epo TEXT
    )
    """)
    
    # 2. Criar tabela de solicitações se não existir
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS solicitacoes (
        id TEXT PRIMARY KEY,
        tipo TEXT NOT NULL,
        especialidade TEXT NOT NULL,
        procedimento TEXT NOT NULL,
        codigo_paciente INTEGER NOT NULL,
        nome_paciente TEXT NOT NULL,
        judicializado TEXT,
        swallis TEXT,
        medico_responsavel TEXT,
        detalhes TEXT,
        tempo_standby INTEGER,
        status TEXT NOT NULL,
        data_criacao TEXT NOT NULL,
        perfil_executor TEXT,
        procedimento_anterior TEXT
    )
    """)
    
    # 3. Criar tabela de status locais se não existir
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS status_locais (
        codigo_paciente INTEGER PRIMARY KEY,
        status_local TEXT NOT NULL,
        data_atualizacao TEXT NOT NULL
    )
    """)
    
    conn.commit()
    
    # --- Migrar Pacientes ---
    if os.path.exists(CSV_PACIENTES):
        print(f"Lendo {CSV_PACIENTES}...")
        with open(CSV_PACIENTES, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                # Converte campo nulo do CSV se aplicável
                cpf = None if row.get('cpf') == '(null)' else row.get('cpf')
                nome_pai = None if row.get('nome_pai') == '(null)' else row.get('nome_pai')
                
                try:
                    cursor.execute("""
                    INSERT OR REPLACE INTO pacientes (
                        codigo, nome, dt_nascimento, cpf, sexo, cor, nome_mae, nome_pai,
                        data_hora_inicio, status_consulta, especialidade, procedimento, ultima_consulta_epo
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        int(row['codigo']),
                        row['nome'],
                        row.get('dt_nascimento'),
                        cpf,
                        row.get('sexo'),
                        row.get('cor'),
                        row.get('nome_mae'),
                        nome_pai,
                        row.get('data_hora_inicio'),
                        row.get('status_consulta'),
                        row.get('especialidade'),
                        row.get('procedimento'),
                        row.get('ultima_consulta_epo')
                    ))
                    count += 1
                except Exception as e:
                    print(f"Erro ao inserir paciente {row.get('codigo')}: {e}")
            print(f"-> {count} pacientes migrados.")
    else:
        print(f"Aviso: {CSV_PACIENTES} não encontrado. Pulando.")
        
    # --- Migrar Solicitações ---
    if os.path.exists(CSV_SOLICITACOES):
        print(f"Lendo {CSV_SOLICITACOES}...")
        with open(CSV_SOLICITACOES, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                try:
                    tempo_standby = int(row['tempo_standby']) if row.get('tempo_standby') else None
                    cursor.execute("""
                    INSERT OR REPLACE INTO solicitacoes (
                        id, tipo, especialidade, procedimento, codigo_paciente, nome_paciente,
                        judicializado, swallis, medico_responsavel, detalhes, tempo_standby,
                        status, data_criacao, perfil_executor, procedimento_anterior
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row['id'],
                        row['tipo'],
                        row['especialidade'],
                        row['procedimento'],
                        int(row['codigo_paciente']),
                        row['nome_paciente'],
                        row.get('judicializado'),
                        row.get('swallis'),
                        row.get('medico_responsavel'),
                        row.get('detalhes'),
                        tempo_standby,
                        row['status'],
                        row['data_criacao'],
                        row.get('perfil_executor'),
                        row.get('procedimento_anterior')
                    ))
                    count += 1
                except Exception as e:
                    print(f"Erro ao inserir solicitação {row.get('id')}: {e}")
            print(f"-> {count} solicitações migradas.")
    else:
        print(f"Aviso: {CSV_SOLICITACOES} não encontrado. Pulando.")

    # --- Migrar Status Locais ---
    if os.path.exists(CSV_STATUS_LOCAIS):
        print(f"Lendo {CSV_STATUS_LOCAIS}...")
        with open(CSV_STATUS_LOCAIS, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                try:
                    cursor.execute("""
                    INSERT OR REPLACE INTO status_locais (
                        codigo_paciente, status_local, data_atualizacao
                    ) VALUES (?, ?, ?)
                    """, (
                        int(row['codigo_paciente']),
                        row['status_local'],
                        row['data_atualizacao']
                    ))
                    count += 1
                except Exception as e:
                    print(f"Erro ao inserir status local para paciente {row.get('codigo_paciente')}: {e}")
            print(f"-> {count} status locais migrados.")
    else:
        print(f"Aviso: {CSV_STATUS_LOCAIS} não encontrado. Pulando.")

    conn.commit()
    conn.close()
    print("Migração concluída com sucesso!")

if __name__ == "__main__":
    migrate()
