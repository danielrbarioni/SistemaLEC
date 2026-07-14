import csv
import os

path = r'c:\Users\daniel.barioni\.gemini\antigravity-ide\scratch\Antigravity IDE\Sistema LEC\data\solicitacoes.csv'

if os.path.exists(path):
    with open(path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, [])
    
    if 'data_acao' not in header:
        solics = []
        with open(path, mode='r', encoding='utf-8') as f:
            r = csv.DictReader(f)
            for row in r:
                if 'data_acao' not in row:
                    # For completed ones, we fallback data_acao to their creation date + 10 mins so they have some time
                    if row.get('status') in ['APROVADO', 'REJEITADO']:
                        row['data_acao'] = row.get('data_criacao', '')
                    else:
                        row['data_acao'] = ''
                solics.append(row)
                
        with open(path, mode='w', encoding='utf-8', newline='') as f:
            fields = ['id', 'tipo', 'especialidade', 'procedimento', 'codigo_paciente', 'nome_paciente', 'judicializado', 'swalis', 'medico_responsavel', 'detalhes', 'tempo_standby', 'status', 'data_criacao', 'perfil_executor', 'procedimento_anterior', 'data_acao']
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(solics)
        print("CSV Migrated successfully.")
    else:
        print("data_acao already exists in CSV.")
else:
    print("CSV file not found.")
