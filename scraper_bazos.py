import requests
from bs4 import BeautifulSoup
import sqlite3
import time

def run_bazos_scraper():
    print("🔵 Spouštím scraper pro Bazoš...")

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

    headers = {"User-Agent": "Mozilla/5.0"}

    base_url = "https://auto.bazos.cz/?hledat=&rubriky=www&hlokalita=&humkreis=25&cenaod=&cenado=&orderby=datum&vypis=detail&strana="
    pages_to_scrape = 5  # nastavíš víc pokud chceš
    count = 0

    for page in range(1, pages_to_scrape + 1):
        print(f"📄 Stahuji stránku {page}...")
        url = base_url + str(page)

        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            listings = soup.select("div.inzeraty a.inzeratynadpis")

            for ad in listings:
                title = ad.text.strip()
                link = "https://auto.bazos.cz" + ad["href"]
                price_elem = ad.find_next("div", class_="inzeratycena")
                price_text = price_elem.text.strip().replace(" ", "").replace("Kč", "") if price_elem else ""
                price = int(price_text) if price_text.isdigit() else None

                # Rozdělení názvu na značku a model
                parts = title.split(" ")
                brand = parts[0] if len(parts) > 0 else ""
                model = parts[1] if len(parts) > 1 else ""
                year = None  # z Bazoš stránek se často nedá zjistit

                cursor.execute("""
                    INSERT INTO vehicles (source, vin, brand, model, year, price, link)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("bazos", None, brand, model, year, price, link))
                count += 1

            conn.commit()
            time.sleep(1)

        except Exception as e:
            print(f"❌ Chyba na stránce {page}: {e}")
            time.sleep(1)

    conn.close()
    print(f"✅ Hotovo! Uloženo {count} inzerátů z bazos.cz.")




