import json
import re
from datetime import datetime
import os
import cloudscraper
from bs4 import BeautifulSoup

FILE_DATI = "dati.json"

scraper = cloudscraper.create_scraper(browser={
    'browser': 'chrome',
    'platform': 'windows',
    'desktop': True
})

def get_octopus():
    url = "https://octopusenergy.it/le-nostre-tariffe?utm_source=Google&utm_medium=Search&utm_campaign=Brand"
    try:
        res = scraper.get(url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        testo = soup.get_text(separator=' ')
        prezzi = re.findall(r"(\d+,\d+)\s*€/kWh", testo)
        return float(prezzi[0].replace(',', '.')) if prezzi else None
    except:
        return None

def get_pun():
    try:
        url_gme = "https://www.mercatoelettrico.org/it/"
        res = scraper.get(url_gme, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        testo = re.sub(r'\s+', ' ', soup.get_text(separator=' '))
        match = re.search(r"PUN Index GME\s*\([^)]+\)\s*(\d+,\d{2})", testo, re.IGNORECASE)
        if match:
            pun_mwh = float(match.group(1).replace(',', '.'))
            return round(pun_mwh / 1000, 4)
    except Exception as e:
        print(f"Piano A fallito: {e}")

    try:
        url_facile = "https://www.facile.it/energia-luce-gas/guida/pun-energia.html"
        res = scraper.get(url_facile, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        testo = re.sub(r'\s+', ' ', soup.get_text(separator=' '))
        match = re.search(r"PUN.{0,200}?(0,\d{3,5})", testo, re.IGNORECASE)
        if match:
            return float(match.group(1).replace(',', '.'))
    except Exception as e:
        print(f"Piano B fallito: {e}")
        
    return None

def get_competitors():
    urls = {
        "sorgenia_luce": "https://www.sorgenia.it/partnership-offerte-sorgenia-luce-gas-casa",
        "nen_luce": "https://nen.it/landing/prezzo-bloccato-dieci-anni",
        "enel_luce": "https://www.enel.it/it-it/offerte-luce?category_uid=MzU3",
        "eon_luce": "https://www.eon-energia.com/luce/casa/offerta-luce-prezzo-fisso-24-mesi.html",
        "plenitude_luce": "https://eniplenitude.com/offerta/casa/gas-e-luce/offerte-energia-elettrica",
        "illumia_luce": "https://www.illumia.it/"
    }
    
    risultati = {}
    for nome, link in urls.items():
        try:
            res = scraper.get(link, timeout=15)
            prezzi = re.findall(r"0,\d{3,5}", res.text)
            if prezzi:
                risultati[nome] = float(prezzi[0].replace(',', '.'))
            else:
                risultati[nome] = None
        except:
            risultati[nome] = None
            
    return risultati

def main():
    print("Avvio scansione massiva dei prezzi...")
    
    octo_luce = get_octopus()
    pun = get_pun()
    concorrenti = get_competitors()
    
    print(f"Dati estratti -> Octopus: {octo_luce}, PUN: {pun}")
    
    oggi = datetime.now().strftime("%Y-%m-%d")
    
    nuovo_dato = {
        "data": oggi,
        "octopus_luce_fissa": octo_luce,
        "pun_mercato": pun,
        "sorgenia_luce": concorrenti.get("sorgenia_luce"),
        "nen_luce": concorrenti.get("nen_luce"),
        "enel_luce": concorrenti.get("enel_luce"),
        "eon_luce": concorrenti.get("eon_luce"),
        "plenitude_luce": concorrenti.get("plenitude_luce"),
        "illumia_luce": concorrenti.get("illumia_luce")
    }
    
    if os.path.exists(FILE_DATI):
        with open(FILE_DATI, "r") as f:
            try:
                storico = json.load(f)
            except:
                storico = []
    else:
        storico = []
        
    if storico and storico[-1]["data"] == oggi:
        storico[-1] = nuovo_dato
        print(f"🔄 Dati di oggi ({oggi}) aggiornati e sovrascritti nel database!")
    else:
        storico.append(nuovo_dato)
        print(f"✅ Nuovi dati aggiunti per il {oggi}!")

    with open(FILE_DATI, "w") as f:
        json.dump(storico, f, indent=2)

if __name__ == "__main__":
    main()
