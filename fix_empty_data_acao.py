import csv
import os

path = r'c:\Users\daniel.barioni\.gemini\antigravity-ide\scratch\Antigravity IDE\Sistema LEC\data\solicitacoes.csv'

if os.path.exists(path):
    solics = []
    with open(path, mode='r', encoding='utf-8') as f:
        r = csv.DictReader(f)
        fields = r.fieldnames
        for row in r:
            if row.get('status') in ['APROVADO', 'REJEITADO'] and not row.get('data_acao'):
                # Popula data_acao com data_criacao se estiver vazio
                row['data_acao'] = row.get('data_criacao', '')
            solics.append(row)
            
    with open(path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(solics)
    print("CSV fixed successfully.")
else:
    print("CSV file not found.")
