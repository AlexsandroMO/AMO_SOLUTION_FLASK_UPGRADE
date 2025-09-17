import sqlite3
import os

DB_NAME_MED = os.path.join(os.path.dirname(__file__), 'meds.db')

conn = sqlite3.connect(DB_NAME_MED)
cursor = conn.cursor()

# Cria tabela users
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

# Cria tabela medications
cursor.execute('''
CREATE TABLE IF NOT EXISTS medications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    total_pills INTEGER NOT NULL,
    pills_per_dose INTEGER NOT NULL,
    times_per_day INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

# Cria tabela timeline
cursor.execute('''
CREATE TABLE IF NOT EXISTS timeline (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    med_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    taken_at TEXT NOT NULL,
    FOREIGN KEY (med_id) REFERENCES medications(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

conn.commit()
conn.close()
print("Banco e tabelas criados com sucesso!")
