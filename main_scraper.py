from subprocess import run

print("Spouštím scraper pro TipCars...")
run(["python", "scraper_tipcars.py"])

print("Spouštím scraper pro Sauto.cz...")
run(["python", "scraper_sauto.py"])

print("Spouštím scraper pro Bazos.cz...")
run(["python", "scraper_bazos.py"])




