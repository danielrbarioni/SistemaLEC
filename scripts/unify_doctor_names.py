"""
Script de Migração e Padronização de Nomes e Médicos no Banco de Dados SQLite.
Padroniza grafias, remove espaços residuais, corrige inversões de campos e equaliza
nomes em caixa alta (UPPERCASE) em 'usuarios' e 'solicitacoes'.

Uso:
    python scripts/unify_doctor_names.py --dry-run
    python scripts/unify_doctor_names.py --execute
"""

import sqlite3
import datetime
import os
import sys

LOCAL_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "app.db"))
REMOTE_DB_PATH = "/var/app/sistemalec/data/app.db"

def get_target_db():
    if os.path.exists(REMOTE_DB_PATH):
        return REMOTE_DB_PATH
    if os.path.exists(LOCAL_DB_PATH):
        return LOCAL_DB_PATH
    raise FileNotFoundError("Banco de dados SQLite não encontrado nem no caminho da VM nem no local.")

def run():
    dry_run = "--dry-run" in sys.argv or "--execute" not in sys.argv
    db_path = get_target_db()
    
    print(f"=== UNIFICAÇÃO DE GRAFIAS E NOMES DE MÉDICOS NO BANCO ===")
    print(f"Banco alvo: {db_path}")
    print(f"Modo: {'DRY RUN (Nenhuma alteração será salva)' if dry_run else 'EXECUÇÃO REAL'}")

    if not dry_run:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        bak_dir = os.path.dirname(db_path)
        backup_path = os.path.join(bak_dir, f"app_backup_before_unify_{ts}.db")
        print(f"\n1. Criando backup seguro em: {backup_path}...")
        src_conn = sqlite3.connect(db_path)
        dst_conn = sqlite3.connect(backup_path)
        src_conn.backup(dst_conn)
        dst_conn.close()
        src_conn.close()
        print(f"   Backup concluído com sucesso ({os.path.getsize(backup_path)} bytes).")
    else:
        print("\n1. [DRY RUN] Pulando criação de backup.")

    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("BEGIN TRANSACTION")

    try:
        # 1. TABELA USUARIOS
        print("\n2. Processando tabela USUARIOS...")
        specific_user_fixes = {
            'natalia.peixoto': 'NATALIA MAIA ESMERALDO PEIXOTO',
            'silvana.florentino': 'SILVANA REZENDE FLORENTINO DA SILVA',
            'luizy.filgueira': 'LUIZY DELCA FILGUEIRA LOPES PORTO DE LIMA',
            'ana.albuquerque': 'ANA BEATRIZ MEDEIROS LINS DE ALBUQUERQUE TAVARES',
            'carlos.alexandre': 'CARLOS ALEXANDRE DE ALBUQUERQUE MARANHÃO',
            'carlos.smacedo': 'CARLOS EDUARDO SOARES DE MACEDO',
            'julia.fernandes.3': 'JÚLIA MIRANDA FERNANDES',
            'ana.serafim': 'ANA CAROLINE PAZ SERAFIM',
            'anitcia.bueno': 'ANITCIA ADENIA BUENO',
            'helena.nagy': 'HELENA JULIANA NAGY',
            'aleide.silva': 'ALEIDE TAVARES E SILVA',
            'kiara.medeiros': 'KIARA KALLINE RODRIGUES VIRGULINO DE MEDEIROS',
            'mariana.gouveia': 'MARIANA DE CARVALHO LEAL GOUVEIA',
            'nicole.moreira': 'NICOLE CARDOSO DE MELO MOREIRA',
            'priscilla.silveira': 'PRISCILLA REGO BARROS DA SILVEIRA',
            'silvio.neto': 'SILVIO DA SILVA CALDAS NETO',
            'thiago.bezerra': 'THIAGO FREIRE PINTO BEZERRA',
            'wendsteyne.lima': 'WENDSTEYNE BARROS DE LIMA',
            'agda.correia': 'AGDA YASMIN FERREIRA CORREIA',
            'Pedro.Oliveira.7': 'PEDRO HENRIQUE DUARTE OLIVEIRA',
            'Ana.Biase': 'ANA BEATRIZ DE BIASE BEZERRA DE MELO',
            'Fernando.Muti': 'FERNANDO MUTI CARVALHO',
            'Lucas.Alves.2': 'LUCAS VELOSO ALVES',
            'Maria.Vieira': 'MARIA CLARA PEREGRINO TORRES VIEIRA DE MELO',
            'Matheus.Henriques': 'MATHEUS LUCAS HENRIQUES SANTOS',
            'Mathias.Cena': 'MATHIAS GOMES DE CENA',
            'magalhaes.flavia': 'FLÁVIA ALMEIDA DE MAGALHÃES',
            'maria.lopes.13': 'MARIA THAIS DE SOUSA LOPES',
            'renata.leite': 'RENATA ABÍLIO DINIZ LEITE MEDEIROS',
        }

        # Inversão de login/nome para maria-pimentel
        cur.execute("SELECT id, username, nome, especialidade FROM usuarios WHERE username = 'MARIA CLARA MONTEIRO BARBOSA PIMENTEL'")
        for row in cur.fetchall():
            u_id, u_usr, u_nome, u_esp = row
            print(f"   [INVERSÃO FIX] ID {u_id} [{u_esp}]: username '{u_usr}' -> 'maria-pimentel.mp', nome '{u_nome}' -> 'MARIA CLARA MONTEIRO BARBOSA PIMENTEL'")
            if not dry_run:
                cur.execute("UPDATE usuarios SET username = 'maria-pimentel.mp', nome = 'MARIA CLARA MONTEIRO BARBOSA PIMENTEL' WHERE id = ?", (u_id,))

        cur.execute("SELECT id, username, nome, especialidade, funcao FROM usuarios")
        all_users = cur.fetchall()
        users_updated = 0
        for u_id, username, nome, esp, func in all_users:
            if username == 'MARIA CLARA MONTEIRO BARBOSA PIMENTEL':
                continue
            orig_nome = nome or ''
            target_nome = specific_user_fixes.get(username)
            if not target_nome:
                clean = ' '.join(orig_nome.strip().split()).upper()
                if clean != orig_nome:
                    target_nome = clean
            if target_nome and target_nome != orig_nome:
                print(f"   [USUARIO] ID {u_id} ({username} | {esp}): '{orig_nome}' -> '{target_nome}'")
                if not dry_run:
                    cur.execute("UPDATE usuarios SET nome = ? WHERE id = ?", (target_nome, u_id))
                users_updated += 1
        print(f"   Total de registros de usuários atualizados: {users_updated}")

        # 2. TABELA SOLICITACOES
        print("\n3. Processando tabela SOLICITACOES (medico_responsavel)...")
        specific_medico_fixes = {
            'NATALIA MAIA ESMERALDO PERIXOTO': 'NATALIA MAIA ESMERALDO PEIXOTO',
            'SILVANA REZENDE FLORENTINO': 'SILVANA REZENDE FLORENTINO DA SILVA',
            'SILVANA REZENDE FLORENTINO ': 'SILVANA REZENDE FLORENTINO DA SILVA',
            'CARLOS EDUARDO SOARES MACEDO': 'CARLOS EDUARDO SOARES DE MACEDO',
            'Bartolomeu Antonio Nascimento Júnior': 'BARTOLOMEU ANTONIO NASCIMENTO JUNIOR',
            'Bartolomeu Antonio Nascimento Jnior': 'BARTOLOMEU ANTONIO NASCIMENTO JUNIOR',
            'Fábio Dias Neves': 'FABIO DIAS NEVES',
            'Fbio Dias Neves': 'FABIO DIAS NEVES',
            'Guilherme Torreão de Sá': 'GUILHERME TORREAO DE SA',
            'Guilherme Torreo de S': 'GUILHERME TORREAO DE SA',
            'Jairo Zacche de Sá': 'JAIRO ZACCHE DE SA',
            'Jairo Zacche de S': 'JAIRO ZACCHE DE SA',
            'Paula Fernanda Pessoa e Silva': 'PAULA FERNANDA PESSOA E SILVA',
            'Pedro Henrique Duarte Oliveira': 'PEDRO HENRIQUE DUARTE OLIVEIRA',
            'Rafael Anlicoara': 'RAFAEL ANLICOARA',
            'Wendsteyne Barros de Lima': 'WENDSTEYNE BARROS DE LIMA',
            'Mcio Brando Vaz Almeida': 'MUCIO BRANDAO VAZ ALMEIDA',
            'Múcio Brandão Vaz Almeida': 'MUCIO BRANDAO VAZ ALMEIDA',
            'JOS CARLOS DE LIMA': 'JOSE CARLOS DE LIMA',
            'José Carlos de Lima': 'JOSE CARLOS DE LIMA',
        }

        cur.execute("SELECT DISTINCT medico_responsavel FROM solicitacoes WHERE medico_responsavel IS NOT NULL AND medico_responsavel != ''")
        solic_rows_updated = 0
        for (med,) in cur.fetchall():
            target = specific_medico_fixes.get(med)
            if not target:
                clean = ' '.join(med.strip().split())
                target = specific_medico_fixes.get(clean)
                if not target and clean != med:
                    target = clean
            if target and target != med:
                cur.execute("SELECT COUNT(*) FROM solicitacoes WHERE medico_responsavel = ?", (med,))
                cnt = cur.fetchone()[0]
                print(f"   [SOLICITACAO] '{med}' ({cnt} linhas) -> '{target}'")
                if not dry_run:
                    cur.execute("UPDATE solicitacoes SET medico_responsavel = ? WHERE medico_responsavel = ?", (target, med))
                solic_rows_updated += cnt
        print(f"   Total de procedimentos/solicitações atualizados: {solic_rows_updated}")

        if dry_run:
            cur.execute("ROLLBACK")
            print("\n[DRY RUN COMPLETO] Nenhuma alteração foi persistida.")
        else:
            cur.execute("COMMIT")
            print("\n[COMMIT REALIZADO COM SUCESSO] Todas as alterações foram persistidas no banco.")
    except Exception as e:
        cur.execute("ROLLBACK")
        print(f"\nERRO CRÍTICO: {e}")
        sys.exit(1)
    finally:
        con.close()

if __name__ == "__main__":
    run()
