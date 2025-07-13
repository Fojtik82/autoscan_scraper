from scraper_tipcars import scrape_tipcars
from scraper_sauto import scrape_sauto
from scraper_bazos import scrape_bazos
import sqlite3
import os

# ✅ Vytvoření připojení k databázi
def create_connection():
    conn = sqlite3.connect("vehicles.db")
    return conn

# ✅ Vytvoření tabulky, pokud neexistuje
def create_table(conn):
    cursor = conn.cursor()
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

# ✅ Uložení záznamů do DB
def save_to_db(conn, records):
    cursor = conn.cursor()
    for rec in records:
        cursor.execute("""
            INSERT INTO vehicles (source, vin, brand, model, year, price, link)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            rec["source"],
            rec["vin"],
            rec["brand"],
            rec["model"],
            rec["year"],
            rec["price"],
            rec["link"]
        ))
    conn.commit()

# ✅ Hlavní spuštění
if _name_ == "_main_":
    conn = create_connection()
    create_table(conn)

    print("Spouštím scraper pro TipCars...")
    records_tipcars = scrape_tipcars(limit=10)
    save_to_db(conn, records_tipcars)
    print(f"✅ Uloženo {len(records_tipcars)} inzerátů z TipCars.cz.")

    print("Spouštím scraper pro Sauto.cz...")
    records_sauto = scrape_sauto(limit=10)
    save_to_db(conn, records_sauto)
    print(f"✅ Uloženo {len(records_sauto)} inzerátů ze Sauto.cz.")

    print("Spouštím scraper pro Bazoš.cz...")
    records_bazos = scrape_bazos(limit=10)
    save_to_db(conn, records_bazos)
    print(f"✅ Uloženo {len(records_bazos)} inzerátů z Bazoš.cz.")

    conn.close()


