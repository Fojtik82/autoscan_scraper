import requests
from bs4 import BeautifulSoup
import sqlite3
import time

conn = sqlite3.connect("vehicles.db")
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
)
""")
conn.commit()

def scrape_tipcars():
    base_url = "https://www.tipcars.com/osobni/?strana="
    headers = {"User-Agent": "Mozilla/5.0"}
    pages_to_scrape = 2  # Necháme teď jen 2 pro test

    for page in range(1, pages_to_scrape + 1):
        url = base_url + str(page)
        print(f"🔄 Načítám stránku {page}: {url}")
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        listings = soup.select("div.card")  # Ověřený nový selektor
        print(f"✅ Na stránce {page} nalezeno {len(listings)} inzerátů")

        for item in listings:
            title_elem = item.find("h2", class_="card__title")
            price_elem = item.find("span", class_="card__price")
            link_elem = item.find("a", class_="card__title")

            if not title_elem or not price_elem or not link_elem:
                continue

            title = title_elem.get_text(strip=True)
            price = price_elem.get_text(strip=True).replace("Kč", "").replace(" ", "").replace("\xa0", "")
            try:
                price = int(price)
            except ValueError:
                price = None

            link = "https://www.tipcars.com" + link_elem.get("href")
            parts = title.split(" ")
            brand = parts[0] if len(parts) > 0 else None
            model = parts[1] if len(parts) > 1 else None

            cursor.execute("""
                INSERT INTO vehicles (source, vin, brand, model, year, price, link)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("tipcars", None, brand, model, None, price, link))

        conn.commit()
        time.sleep(1)

    print("🎉 Hotovo! Uloženo z TipCars.")

scrape_tipcars()
conn.close()
