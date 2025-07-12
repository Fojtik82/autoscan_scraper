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

headers = {
    "User-Agent": "Mozilla/5.0"
}

def scrape_sauto():
    base_url = "https://www.sauto.cz/osobni?strana="
    pages_to_scrape = 1000  # 20 000 inzerátů = 1000 stránek po 20 vozech
    count = 0

    for page in range(1, pages_to_scrape + 1):
        url = base_url + str(page)
        print(f"📄 Načítám stránku {page} — {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            listings = soup.find_all("div", class_="c-item__content")

            for item in listings:
                title_elem = item.find("a", class_="c-item__link")
                price_elem = item.find("div", class_="c-item__price")
                link = "https://www.sauto.cz" + title_elem["href"] if title_elem else ""
                title = title_elem.text.strip() if title_elem else ""
                price = price_elem.text.strip().replace(" Kč", "").replace(" ", "").replace("\xa0", "") if price_elem else ""
                price = int(price) if price.isdigit() else None

                # Předpokládaná struktura: "Škoda Octavia 1.6 TDI" => značka = Škoda, model = Octavia
                parts = title.split()
                brand = parts[0] if len(parts) > 0 else ""
                model = parts[1] if len(parts) > 1 else ""
                year = ""  # Rok není hned dostupný na přehledu

                cursor.execute("""
                    INSERT INTO vehicles (source, vin, brand, model, year, price, link)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("sauto", None, brand, model, year, price, link))
                count += 1

            conn.commit()
            time.sleep(1)

        except Exception as e:
            print(f"❌ Chyba na stránce {page}: {e}")
            time.sleep(3)

    print(f"✅ Hotovo! Uloženo {count} inzerátů ze Sauto.cz.")

scrape_sauto()



