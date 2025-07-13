import requests
from bs4 import BeautifulSoup
import sqlite3
import time

BASE_URL = "https://www.sauto.cz/osobni?strana="
DB_PATH = "vehicles.db"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "cs-CZ,cs;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

def create_connection():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vin TEXT,
            title TEXT,
            price INTEGER,
            url TEXT,
            source TEXT
        )
    """)
    conn.commit()
    return conn

def save_vehicle(conn, title, price, url):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO vehicles (vin, title, price, url, source)
        VALUES (?, ?, ?, ?, ?)
    """, (None, title, price, url, "sauto"))
    conn.commit()

def scrape_page(page_num, conn):
    url = BASE_URL + str(page_num)
    print(f"🔄 Načítám stránku {page_num}: {url}")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    listings = soup.find_all("div", class_="offer")  # nový selektor
    if not listings:
        print(f"⚠️ Stránka {page_num} – žádné inzeráty")
        return 0

    count = 0
    for item in listings:
        title_elem = item.find("h2")
        price_elem = item.find("div", class_="price")

        if not title_elem or not price_elem:
            continue

        title = title_elem.text.strip()
        price_text = price_elem.text.strip().replace(" ", "").replace("Kč", "").replace("\xa0", "")
        try:
            price = int(price_text)
        except ValueError:
            price = None

        link_tag = title_elem.find("a")
        link = "https://www.sauto.cz" + link_tag["href"] if link_tag else ""

        save_vehicle(conn, title, price, link)
        count += 1
        print(f"✅ {title} – {price} Kč")

    print(f"✅ Stránka {page_num} – nalezeno {count} inzerátů")
    return count

def main():
    conn = create_connection()
    max_pages = 100
    total = 0

    for page in range(1, max_pages + 1):
        count = scrape_page(page, conn)
        if count == 0:
            break
        total += count
        time.sleep(1)

    conn.close()
    print(f"\n🎉 Hotovo! Uloženo {total} inzerátů ze Sauto.cz.")

if __name__ == "__main__":
    main()
