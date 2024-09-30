#fetch_data.py

import sqlite3
import pandas as pd
import json

# Lade Konfiguration
with open('processing_config.json') as config_file:
    config = json.load(config_file)

# Verbindung zur SQLite-Datenbank herstellen
conn = sqlite3.connect(config['db_path'])

# Abfrage durchführen
query = f"""
SELECT * FROM ohlc_data 
WHERE symbol = '{config['symbol']}' 
AND date BETWEEN '{config['start_date']}' AND '{config['end_date']}'
"""
df = pd.read_sql_query(query, conn)
conn.close()

# Daten speichern (optional)
df.to_csv(config['csv_output_path'], index=False)
