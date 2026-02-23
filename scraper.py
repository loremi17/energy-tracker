import json
from datetime import datetime
import os

# Definiamo il file dei dati
FILE_DATI = "dati.json"

# 1. Simuliamo l'estrazione dei dati (qui metteremo il vero scraper)
prezzo_octopus_luce = 0.1045 # Fittizio per ora
prezzo_octopus_gas = 0.3650  # Fittizio per ora
prezzo_pun = 0.0950          # Fittizio per ora
oggi = datetime.now().strftime("%Y-%m-%d")

nuovo_dato = {
    "data": oggi,
    "octopus_luce_fissa": prezzo_octopus_luce,
    "octopus_gas_fissa": prezzo_octopus_gas,
    "pun_mercato": prezzo_pun
}

# 2. Carichiamo lo storico esistente
if os.path.exists(FILE_DATI):
    with open(FILE_DATI, "r") as f:
        storico = json.load(f)
else:
    storico = []

# Evitiamo di duplicare i dati se lo script gira due volte nello stesso giorno
if non storico or storico[-1]["data"] != oggi:
    storico.append(nuovo_dato)
    
    # 3. Salviamo il file aggiornato
    with open(FILE_DATI, "w") as f:
        json.dump(storico, f, indent=2)
    print(f"Dati aggiornati con successo per il {oggi}!")
else:
    print(f"Dati per il {oggi} già presenti. Nessuna modifica.")
