import requests
from bs4 import BeautifulSoup
import sqlite3

DB_FILE = "vehicles.db"

def create_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vin TEXT,
            title TEXT,
            price TEXT,
            url TEXT,
            source TEXT
        )
    """)
    conn.commit()
    conn.close()

def scrape_tipcars(pages=200):
    base_url = "https://www.tipcars.com/osobni-auto/?strana="
    all_vehicles = []

    for page in range(1, pages + 1):
        print(f"Stahuji stránku {page}...")
        url = f"{base_url}{page}"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        ads = soup.find_all("div", class_="card-body")
        for ad in ads:
            title = ad.find("h2")
            price = ad.find("div", class_="price")
            link = ad.find("a", href=True)

            if title and price and link:
                vin = ""  # TipCars VIN přímo neukazuje, může se doplnit později
                all_vehicles.append((
                    vin,
                    title.text.strip(),
                    price.text.strip(),
                    f"https://www.tipcars.com{link['href']}",
                    "tipcars"
                ))

    save_to_db(all_vehicles)

def save_to_db(vehicles):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    for v in vehicles:
        c.execute("""
            INSERT INTO vehicles (vin, title, price, url, source)
            VALUES (?, ?, ?, ?, ?)
        """, v)
    conn.commit()
    conn.close()
    print(f"Uloženo {len(vehicles)} inzerátů.")

if __name__ == "__main__":
    create_db()
    scrape_tipcars(pages=200)

