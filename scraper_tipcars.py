import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(search_url)

    html = driver.page_source

    # Uložit HTML pro debug
    with open("debug.html", "w", encoding="utf-8") as f:
        f.write(html)

    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    listings = soup.find_all("a", class_="card", limit=limit)

    results = []
    for item in listings:
        link = base_url + item.get("href")
        title_elem = item.find("h2")
        price_elem = item.find("div", class_="price")

        title = title_elem.text.strip() if title_elem else ""
        price = price_elem.text.strip().replace(" Kč", "").replace(" ", "") if price_elem else "0"

        brand, model, year =
