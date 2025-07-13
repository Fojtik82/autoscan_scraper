import sqlite3

def create_database():
    # Připojení k databázi (vytvoří se pokud neexistuje)
    conn = sqlite3.connect("vehicles.db")
    cursor = conn.cursor()

    # Vytvoření tabulky vehicles, pokud ještě neexistuje
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
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Databáze vehicles.db byla připravena.")

if _name_ == "_main_":
    create_database()
