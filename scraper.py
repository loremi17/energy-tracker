import json
import re
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup

# Definiamo il file dei dati
FILE_DATI = "dati.json"

def get_octopus_prices():
    url = "https://octopusenergy.it/le-nostre-tariffe?utm_source=Google&utm_medium=Search&utm_campaign=Brand"
    
    # Camuffiamo la nostra richiesta per sembrare un browser normale, altrimenti i siti ci bloccano
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # Scarichiamo la pagina
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Controlla che non ci siano errori (es. pagina non trovata)
        
        # Analizziamo l'HTML e ne estraiamo solo il testo pulito
        soup = BeautifulSoup(response.text, 'html.parser')
        testo_pagina = soup.get_text(separator=' ')
        
        # --- ESTRAZIONE TRAMITE REGEX ---
        # Cerchiamo tutti i pattern del tipo "numero,numero €/kWh" e "numero,numero €/Smc"
        # \d+,\d+ significa "uno o più numeri, una virgola, uno o più numeri"
        prezzi_luce = re.findall(r"(\d+,\d+)\s*€/kWh", testo_pagina)
        prezzi_gas = re.findall(r"(\d+,\d+)\s*€/Smc", testo_pagina)
        
        # In base alla struttura attuale del sito:
        # Il 1° valore trovato è la tariffa Fissa, il 2° è lo spread della tariffa Flex.
        # Li convertiamo in numeri decimali (sostituendo la virgola col punto)
        luce_fissa = float(prezzi_luce[0].replace(',', '.')) if prezzi_luce else None
        luce_flex_spread = float(prezzi_luce[1].replace(',', '.')) if len(prezzi_luce) > 1 else None
        
        gas_fissa = float(prezzi_gas[0].replace(',', '.')) if prezzi_gas else None
        gas_flex_spread = float(prezzi_gas[1].replace(',', '.')) if len(prezzi_gas) > 1 else None
        
        return luce_fissa, gas_fissa, luce_flex_spread, gas_flex_spread
        
    except Exception as e:
        print(f"Errore durante lo scraping: {e}")
        return None, None, None, None

def main():
    print("Avvio scraping Octopus Energy...")
    luce_fissa, gas_fissa, luce_flex_spread, gas_flex_spread = get_octopus_prices()
    
    if luce_fissa is None:
        print("Impossibile recuperare i dati dal sito. Lo script si ferma per non corrompere il grafico.")
        return

    # Per ora usiamo un PUN/PSV fisso. Il prossimo step sarà automatizzare anche questo!
    pun_mercato = 0.0950 
    psv_mercato = 0.3500
    
    oggi = datetime.now().strftime("%Y-%m-%d")
    
    nuovo_dato = {
        "data": oggi,
        "octopus_luce_fissa": luce_fissa,
        "octopus_gas_fissa": gas_fissa,
        "octopus_luce_flex_spread": luce_flex_spread,
        "octopus_gas_flex_spread": gas_flex_spread,
        "pun_mercato": pun_mercato,
        "psv_mercato": psv_mercato
    }
    
    # Carichiamo lo storico esistente
    if os.path.exists(FILE_DATI):
        with open(FILE_DATI, "r") as f:
            try:
                storico = json.load(f)
            except json.JSONDecodeError:
                storico = []
    else:
        storico = []
        
    # Evitiamo doppioni: se l'ultimo dato in memoria NON è di oggi, lo aggiungiamo
    if not storico or storico[-1]["data"] != oggi:
        storico.append(nuovo_dato)
        
        # Salviamo il file aggiornato
        with open(FILE_DATI, "w") as f:
            json.dump(storico, f, indent=2)
        print(f"✅ Dati salvati con successo per il {oggi}!")
        print(f"Luce Fissa: {luce_fissa} €/kWh | Gas Fissa: {gas_fissa} €/Smc")
    else:
        print(f"⚠️ Dati per il {oggi} già presenti. Nessuna modifica apportata.")

if __name__ == "__main__":
    main()
