import os
import uuid
import sqlite3
import pandas as pd

DB_PATH = 'data/app.db'
FILE_FILA = 'data/Fila sistema Sede Plástica.xlsx'
FILE_PROCS = 'data/Procedimentos Plástica.xlsx'

def run_import():
    if not os.path.exists(FILE_FILA) or not os.path.exists(FILE_PROCS):
        print("Erro: Planilhas não encontradas na pasta data/")
        return

    print("1. Lendo planilhas Excel...")
    df_fila = pd.read_excel(FILE_FILA)
    df_procs = pd.read_excel(FILE_PROCS)

    print(f"Fila: {len(df_fila)} linhas | Procedimentos: {len(df_procs)} linhas")

    # Merge das planilhas pelo id_procedimento
    df_merged = df_fila.merge(df_procs, on='id_procedimento', how='inner')
    print(f"Registros vinculados após merge: {len(df_merged)}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Garantir a criação das tabelas se não existirem
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS perfis (
        id TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        tipo TEXT NOT NULL,
        cor TEXT NOT NULL,
        especialidade TEXT
    );
    """)

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
    );
    """)

    # 1. Garantir perfil PLASTICA
    cursor.execute("SELECT id FROM perfis WHERE id = 'PLASTICA'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO perfis (id, nome, tipo, cor, especialidade) VALUES (?, ?, ?, ?, ?)",
            ('PLASTICA', 'PLÁSTICA', 'ESPECIALIDADE', 'verde', 'Plástica')
        )
        print("Perfil 'PLÁSTICA' cadastrado.")
    else:
        print("Perfil 'PLÁSTICA' já existente.")

    # 2. Inserir Pacientes e Solicitações
    count_pac = 0
    count_sol = 0

    for idx, row in df_merged.iterrows():
        prontuario = int(row['prontuario'])
        proc_desc = str(row['PROCEDIMENTO']).strip()
        medico = str(row['medico_responsavel']).strip() if pd.notna(row['medico_responsavel']) else 'Não informado'
        swalis = str(row['swalis']).strip() if pd.notna(row['swalis']) else '—'
        judicializado = 'Sim' if bool(row['sin_judicializado']) else 'Não'
        
        # Formatação da data
        dth_val = row['dth_indicacao']
        if pd.notna(dth_val):
            dth_str = str(dth_val).replace(' ', 'T')
        else:
            dth_str = '2024-01-01T00:00:00'

        nome_paciente = f"Paciente #{prontuario}"

        # Insert paciente se não existir
        cursor.execute("SELECT codigo FROM pacientes WHERE codigo = ?", (prontuario,))
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO pacientes (
                codigo, nome, dt_nascimento, nome_mae, especialidade, procedimento
            ) VALUES (?, ?, ?, ?, ?, ?)
            """, (prontuario, nome_paciente, '—', '—', 'Plástica', proc_desc))
            count_pac += 1

        # Insert solicitação aprovada
        sol_id = uuid.uuid4().hex[:8]
        cursor.execute("""
        INSERT INTO solicitacoes (
            id, tipo, especialidade, procedimento, codigo_paciente, nome_paciente,
            judicializado, swallis, medico_responsavel, detalhes, status,
            data_criacao, perfil_executor, usuario, origem_menu
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sol_id,
            'INSERIR',
            'Plástica',
            proc_desc,
            prontuario,
            nome_paciente,
            judicializado,
            swalis,
            medico,
            'Importado da Sede (Plástica)',
            'APROVADO',
            dth_str,
            'GESTAO_LEC',
            'sistema.sede',
            'ACOMPANHAMENTO'
        ))
        count_sol += 1

    conn.commit()
    conn.close()
    print(f"\nImportação concluída!")
    print(f"-> {count_pac} novos pacientes inseridos em 'pacientes'")
    print(f"-> {count_sol} solicitações inseridas em 'solicitacoes'")

if __name__ == '__main__':
    run_import()
