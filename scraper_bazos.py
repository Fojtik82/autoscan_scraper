import requests
from bs4 import BeautifulSoup
import sqlite3
import time

# Připojení k databázi
conn = sqlite3.connect("vehicles.db")
cursor = conn.cursor()

# Vytvoření tabulky, pokud ještě neexistuje
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

def scrape_bazos():
    base_url = "https://auto.bazos.cz/osobni/?hledat=&razeni=1&hlokalita=&humkreis=0&cenaod=&cenado=&order=1&strana="
    headers = {"User-Agent": "Mozilla/5.0"}
    pages_to_scrape = 50
    count = 0

    for page in range(1, pages_to_scrape + 1):
        url = base_url + str(page)
        print(f"Načítám stránku {page} - {url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            listings = soup.find_all("div", class_="inzeraty")

            for container in listings:
                rows = container.find_all("div", class_="inzeratynadpis")
                for item in rows:
                    title_elem = item.find("a")
                    price_elem = item.find_next("div", class_="inzeratycena")

                    if not title_elem or not price_elem:
                        continue

                    title = title_elem.text.strip()
                    link = title_elem.get("href")
                    if not link.startswith("http"):
                        link = "https://auto.bazos.cz" + link
                    price = price_elem.text.strip().replace(" Kč", "").replace(" ", "")

                    parts = title.split()
                    brand = parts[0] if len(parts) > 0 else None
                    model = parts[1] if len(parts) > 1 else None

                    cursor.execute("""
                        INSERT INTO vehicles (source, vin, brand, model, year, price, link)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, ("bazos", None, brand, model, None, int(price) if price.isdigit() else None, link))

                    count += 1

            conn.commit()
            time.sleep(1)

        except Exception as e:
            print(f"\u274c Chyba na stránce {page}: {e}")
            time.sleep(2)

    print(f"\u2705 Hotovo! Uloženo {count} inzerátů z Bazoš.cz.")

scrape_bazos()
conn.close()
