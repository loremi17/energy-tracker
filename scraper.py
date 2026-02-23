import json
import re
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup

FILE_DATI = "dati.json"

# Header finto per far credere ai siti di essere un browser reale
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7"
}

def get_octopus():
    url = "https://octopusenergy.it/le-nostre-tariffe?utm_source=Google&utm_medium=Search&utm_campaign=Brand"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        testo = soup.get_text(separator=' ')
        prezzi = re.findall(r"(\d+,\d+)\s*€/kWh", testo)
        return float(prezzi[0].replace(',', '.')) if prezzi else None
    except:
        return None

def get_pun():
    # Per il PUN usiamo un portale informativo affidabile e statico (Luce-gas.it o MercatoElettrico)
    url = "https://luce-gas.it/guida/mercato/pun"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        # Cerchiamo un prezzo tipico del PUN (es. 0,09 o 0,10) nel testo
        match = re.search(r"0,\d{3,5}", res.text)
        return float(match.group(0).replace(',', '.')) if match else None
    except:
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
            res = requests.get(link, headers=HEADERS, timeout=15)
            # Cerchiamo un formato prezzo del tipo 0,1234
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
    
    oggi = datetime.now().strftime("%Y-%m-%d")
    
    # Costruiamo l'oggetto del giorno
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
    
    # Carichiamo i dati esistenti
    if os.path.exists(FILE_DATI):
        with open(FILE_DATI, "r") as f:
            try:
                storico = json.load(f)
            except:
                storico = []
    else:
        storico = []
        
    # Salviamo (evitando doppioni nello stesso giorno)
    if not storico or storico[-1]["data"] != oggi:
        storico.append(nuovo_dato)
        with open(FILE_DATI, "w") as f:
            json.dump(storico, f, indent=2)
        print(f"✅ Dati estratti e salvati per il {oggi}:")
        print(json.dumps(nuovo_dato, indent=2))
    else:
        print("⚠️ Dati di oggi già presenti. Aggiornamento saltato.")

if __name__ == "__main__":
    main()
