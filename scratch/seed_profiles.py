import sqlite3

def run():
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Insert GESTAO_LEC
    cursor.execute("SELECT id FROM perfis WHERE id = 'GESTAO_LEC'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO perfis (id, nome, tipo, cor, especialidade) VALUES (?, ?, ?, ?, ?)",
                       ('GESTAO_LEC', 'GESTÃO LEC', 'GESTAO_LEC', 'azul', None))
        print("Inserted GESTÃO LEC profile.")
    else:
        print("GESTÃO LEC profile already exists.")

    # Insert PLASTICA
    cursor.execute("SELECT id FROM perfis WHERE id = 'PLASTICA'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO perfis (id, nome, tipo, cor, especialidade) VALUES (?, ?, ?, ?, ?)",
                       ('PLASTICA', 'PLÁSTICA', 'ESPECIALIDADE', 'verde', 'Plástica'))
        print("Inserted ESPECIALIDADE - Plástica profile.")
    else:
        print("ESPECIALIDADE - Plástica profile already exists.")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    run()
