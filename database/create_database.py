import sqlite3
import json
from google.colab import drive

# Lade Konfiguration
with open('db_config.json') as config_file:
    config = json.load(config_file)

# Mount Google Drive
drive.mount('/content/drive')

# Verbindung zur SQLite-Datenbank herstellen
conn = sqlite3.connect(config['db_path'])
cursor = conn.cursor()

# Tabelle erstellen und Daten einfügen (Beispiel)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS ohlc_data (
        symbol TEXT,
        date TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume REAL
    )
''')

# Beispielhafte Daten einfügen
data = [
    ('BTC/USD', '2023-08-01', 29000, 29500, 28900, 29400, 1000),
    # Weitere Daten ...
]
cursor.executemany('INSERT INTO ohlc_data VALUES (?, ?, ?, ?, ?, ?, ?)', data)
conn.commit()
conn.close()
