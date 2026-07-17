import sqlite3

def run():
    conn = sqlite3.connect('data/app.db')
    conn.execute("UPDATE perfis SET nome = 'ADMIN' WHERE id = 'ADMIN'")
    conn.commit()
    conn.close()
    print("Database updated: Admin profile name is now 'ADMIN'.")

if __name__ == '__main__':
    run()
