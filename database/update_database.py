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

# Beispielhafte Datenaktualisierung
new_data = [
    ('BTC/USD', '2023-08-02', 29400, 29800, 29200, 29700, 1100),
    # Weitere Daten ...
]
cursor.executemany('INSERT INTO ohlc_data VALUES (?, ?, ?, ?, ?, ?, ?)', new_data)
conn.commit()
conn.close()
