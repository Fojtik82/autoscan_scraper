import sqlite3

# Připojení k databázi
conn = sqlite3.connect("vehicles.db")
cursor = conn.cursor()

# Vytvoření tabulky
cursor.execute("""
CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    vin TEXT,
    brand TEXT,
    model TEXT,
    year TEXT,
    price INTEGER,
    link TEXT
);
""")

conn.commit()
conn.close()

print("Databáze vehicles.db byla připravena.")
