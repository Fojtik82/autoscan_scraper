import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

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
        )
    """)
    conn.commit()

def scrape_tipcars(limit=10):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    base_url = "https://www.tipcars.com/osobni/?strana="
    results = []

    page = 1
    while len(results) < limit:
        driver.get(base_url + str(page))
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        listings = soup.find_all("a", class_="card")

        if not listings:
            break

        for item in listings:
            if len(results) >= limit:
                break
            link = "https://www.tipcars.com" + item.get("href")
            title_elem = item.find("h2")
            price_elem = item.find("div", class_="price")

            title = title_elem.text.strip() if title_elem else ""
            price = price_elem.text.strip().replace(" Kč", "").replace(" ", "") if price_elem else "0"
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

        page += 1

    driver.quit()
    return results

def save_to_db(conn, records):
    cursor = conn.cursor()
    for rec in records:
        cursor.execute("""
            INSERT INTO vehicles (source, vin, brand, model, year, price, link)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (rec['source'], rec['vin'], rec['brand'], rec['model'], rec['year'], rec['price'], rec['link']))
    conn.commit()

if _name_ == "_main_":
    conn = create_connection()
    create_table(conn)
    records = scrape_tipcars(limit=10)
    save_to_db(conn, records)
    print(f"Uloženo {len(records)} záznamů do databáze")
