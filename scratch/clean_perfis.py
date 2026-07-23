import sqlite3

def run():
    conn = sqlite3.connect('data/app.db')
    c = conn.cursor()
    c.execute('SELECT id, nome, tipo, cor, especialidade FROM perfis')
    print('BEFORE:', c.fetchall())

    c.execute("DELETE FROM perfis WHERE id != 'PLASTICA' AND (id LIKE '%PL%STICA%' OR nome LIKE '%PL%STICA%')")

    c.execute("""
    INSERT INTO perfis (id, nome, tipo, cor, especialidade)
    VALUES ('PLASTICA', 'PLÁSTICA', 'ESPECIALIDADE', 'verde', 'Plástica')
    ON CONFLICT(id) DO UPDATE SET
      nome = 'PLÁSTICA',
      tipo = 'ESPECIALIDADE',
      cor = 'verde',
      especialidade = 'Plástica'
    """)

    conn.commit()

    c.execute('SELECT id, nome, tipo, cor, especialidade FROM perfis')
    print('AFTER:', c.fetchall())
    conn.close()

if __name__ == '__main__':
    run()
