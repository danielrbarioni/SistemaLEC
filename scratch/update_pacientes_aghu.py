import os
import sqlite3
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_PATH = 'data/app.db'
POSTGRES_DSN = os.getenv('POSTGRES_DSN', '')

def run_update():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('SELECT codigo FROM pacientes')
    prontuarios = [row[0] for row in c.fetchall()]
    print(f"Total de pacientes no SQLite local: {len(prontuarios)}")

    if not POSTGRES_DSN:
        print("POSTGRES_DSN não configurado no .env. Pulando atualização do AGHU.")
        conn.close()
        return

    # Tenta conectar no PostgreSQL do AGHU
    dsn_clean = POSTGRES_DSN.replace('postgresql+asyncpg://', 'postgresql://')
    try:
        pg_conn = psycopg2.connect(dsn_clean, connect_timeout=5)
        pg_cur = pg_conn.cursor()
        print("Conectado com sucesso ao PostgreSQL do AGHU!")

        # Buscar dados em lotes
        chunk_size = 500
        total_updated = 0

        for i in range(0, len(prontuarios), chunk_size):
            chunk = prontuarios[i:i + chunk_size]
            query = """
                SELECT prontuario, nome, dt_nascimento, nome_mae, cpf, sexo
                FROM agh.aip_pacientes
                WHERE prontuario IN %s
            """
            pg_cur.execute(query, (tuple(chunk),))
            rows = pg_cur.fetchall()

            for row in rows:
                p_code, p_nome, p_nasc, p_mae, p_cpf, p_sexo = row
                p_nasc_str = str(p_nasc) if p_nasc else '—'
                p_mae_str = p_mae if p_mae else '—'
                p_cpf_str = str(p_cpf) if p_cpf else None
                p_sexo_str = str(p_sexo) if p_sexo else None

                # Atualiza pacientes
                c.execute("""
                    UPDATE pacientes
                    SET nome = ?, dt_nascimento = ?, nome_mae = ?, cpf = COALESCE(?, cpf), sexo = COALESCE(?, sexo)
                    WHERE codigo = ?
                """, (p_nome, p_nasc_str, p_mae_str, p_cpf_str, p_sexo_str, p_code))

                # Atualiza solicitações
                c.execute("""
                    UPDATE solicitacoes
                    SET nome_paciente = ?
                    WHERE codigo_paciente = ?
                """, (p_nome, p_code))

                total_updated += 1

        conn.commit()
        pg_conn.close()
        print(f"Atualização concluída: {total_updated} pacientes sincronizados com o AGHU.")

    except Exception as e:
        print(f"Não foi possível conectar ao PostgreSQL do AGHU: {e}")
        print("O sistema continuará utilizando os dados mantidos no SQLite local.")
    finally:
        conn.close()

if __name__ == '__main__':
    run_update()
