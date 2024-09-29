import pandas as pd
import json

# Lade Konfiguration
with open('processing_config.json') as config_file:
    config = json.load(config_file)

# Laden der CSV-Daten
df = pd.read_csv(config['csv_output_path'])

# Speichern als Parquet
df.to_parquet(config['parquet_output_path'], index=False)
