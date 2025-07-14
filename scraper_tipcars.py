from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import sqlite3

def create_connection():
    return sqlite3.connect("vehicles.db")

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
        )
    """)
    conn.commit()

def scrape_tipcars(limit=10):
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for page_num in range(1, limit + 1):
            url = f"https://www.tipcars.com/vozy/?strana={page_num}"
            page.goto(url)
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
            items = soup.select("a.ListItem")  # může být potřeba upravit dle struktury
            for item in items:
                brand = item.select_one(".ListItemTitle-makeModel").text.strip() if item.select_one(".ListItemTitle-makeModel") else ""
                model = ""
                year = item.select_one(".ListItemParameter-year").text.strip() if item.select_one(".ListItemParameter-year") else ""
                price_raw = item.select_one(".ListItemPrice").text.strip().replace(" ", "").replace("Kč", "") if item.select_one(".ListItemPrice") else "0"
                price = int("".join(filter(str.isdigit, price_raw)))
                link = "https://www.tipcars.com" + item["href"]
                results.append({
                    "source": "tipcars",
                    "vin": "",
                    "brand": brand,
                    "model": model,
                    "year": year,
                    "price": price,
                    "link": link
                })
        browser.close()
    return results

def save_to_db(conn, records):
    cursor = conn.cursor()
    for rec in records:
        cursor.execute("""
            INSERT INTO vehicles (source, vin, brand, model, year, price, link)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            rec["source"], rec["vin"], rec["brand"], rec["model"],
            rec["year"], rec["price"], rec["link"]
        ))
    conn.commit()

if __name__ == "__main__":
    conn = create_connection()
    create_table(conn)
    records = scrape_tipcars(limit=2)  # můžeš zvýšit třeba na 100
    save_to_db(conn, records)
    print(f"Uloženo {len(records)} záznamů do databáze.")
