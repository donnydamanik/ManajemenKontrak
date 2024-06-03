import sqlite3

def init_db():
    conn = sqlite3.connect('contracts.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        end_date DATE NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
