import sqlite3
import requests
from bs4 import BeautifulSoup

def create_connection():
    conn = sqlite3.connect("vehicles.db")
    return conn

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

def scrape_tipcars(limit=10):
    base_url = "https://www.tipcars.com"
    search_url = "https://www.tipcars.com/osobni"
    results = []

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    listings = soup.find_all("a", class_="card", limit=limit)

    for item in listings:
        link = base_url + item.get("href")
        title_elem = item.find("h2")
        price_elem = item.find("div", class_="price")

        title = title_elem.text.strip() if title_elem else ""
        price = price_elem.text.strip().replace(" Kč", "").replace(" ", "") if price_elem else 0

        brand, model, year = (title.split(" ") + [None]*3)[:3]
        results.append({
            "source": "tipcars",
            "vin": "",
            "brand": brand or "",
            "model": model or "",
            "year": year or "",
            "price": int(price) if price.isdigit() else 0,
            "link": link
        })
    return results

def save_to_db(conn, records):
    cursor = conn.cursor()
    for rec in records:
        cursor.execute("""
            INSERT INTO vehicles (source, vin, brand, model, year, price, link)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (rec['source'], rec['vin'], rec['brand'], rec['model'], rec['year'], rec['price'], rec['link']))
    conn.commit()

if __name__ == "__main__":
    conn = create_connection()
    create_table(conn)
    records = scrape_tipcars(limit=10)
    save_to_db(conn, records)
    print(f"Uloženo {len(records)} záznamů do databáze.")
