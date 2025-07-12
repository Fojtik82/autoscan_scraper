
# main_scraper.py

import subprocess

def run_scraper(script_name):
    try:
        print(f"Spouštím: {script_name}")
        subprocess.run(["python", script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Chyba při spuštění {script_name}: {e}")

if __name__ == "__main__":
    scrapers = ["scraper_tipcars.py", "scraper_sauto.py", "scraper_bazos.py"]

    for scraper in scrapers:
        run_scraper(scraper)



