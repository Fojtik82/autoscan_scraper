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

def scrape_tipcars():
    base_url = "https://www.tipcars.com/osobni/?strana="
    headers = {"User-Agent": "Mozilla/5.0"}
    pages_to_scrape = 100
    count = 0

    for page in range(1, pages_to_scrape + 1):
        url = base_url + str(page)
        print(f"Načítám stránku {page} - {url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            listings = soup.find_all("div", class_="tc-card")

            for item in listings:
                title_elem = item.find("h2", class_="tc-card__title")
                price_elem = item.find("span", class_="tc-card__price")
                link_elem = item.find("a", class_="tc-card__title")

                if not title_elem or not price_elem or not link_elem:
                    continue

                title = title_elem.text.strip()
                price = price_elem.text.strip().replace(" \u20ac", "").replace(" ", "")
                link = "https://www.tipcars.com" + link_elem.get("href")

                parts = title.split()
                brand = parts[0] if len(parts) > 0 else None
                model = parts[1] if len(parts) > 1 else None

                cursor.execute("""
                    INSERT INTO vehicles (source, vin, brand, model, year, price, link)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("tipcars", None, brand, model, None, int(price) if price.isdigit() else None, link))

                count += 1

            conn.commit()
            time.sleep(1)

        except Exception as e:
            print(f"\u274c Chyba na stránce {page}: {e}")
            time.sleep(2)

    print(f"\u2705 Hotovo! Uloženo {count} inzerátů z TipCars.cz.")

scrape_tipcars()
conn.close()



