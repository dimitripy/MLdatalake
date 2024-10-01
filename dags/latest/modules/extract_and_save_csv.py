import pandas as pd
from zipfile import ZipFile
import json
import yaml
import os

def extract_and_save_csv(zip_file_path, output_csv_path):
    with ZipFile(zip_file_path) as zf:
        cols = ['time', 'open', 'high', 'low', 'close', 'volume']
        dfs = pd.concat({text_file.filename.split('.')[0]: pd.read_csv(zf.open(text_file.filename), usecols=cols)
            for text_file in zf.infolist() if text_file.filename.endswith('.csv')})
    
    df = dfs.droplevel(1).reset_index().rename(columns={'index': 'ticker'})
    df = df[df['ticker'].str.contains('usd')]
    df['date'] = pd.to_datetime(df['time'], unit='ms')
    df = df.sort_values(by=['date', 'ticker']).drop(columns='time').set_index(['date', 'ticker'])
    
    df.to_csv(output_csv_path)
    print(f"CSV-Datei wurde erfolgreich unter {output_csv_path} gespeichert.")

if __name__ == "__main__":
    # Pfad zur config.json Datei
    config_path = '/opt/airflow/dags/mldatalake/latest/config.json'
    
    # Einlesen der Konfigurationsdatei
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    
    # Extrahieren des Dateinamens aus der JSON-Datei
    zip_file_name = config['zip_file_name']
    
    # Pfad zur Registry-Datei
    registry_file_path = '/etc/airflow/airflow_dag_registry.yaml'
    
    # Einlesen der Registry-Datei
    with open(registry_file_path, 'r') as registry_file:
        registry = yaml.safe_load(registry_file)
    
    # Extrahieren des Pfades aus der Registry-Datei
    registry_path = registry['path_to_registry']
    
    # Erstellen des vollständigen Pfades zur ZIP-Datei im source-Verzeichnis
    source_dir = os.path.join(os.path.dirname(registry_path), 'source')
    zip_file_path = os.path.join(source_dir, f"{zip_file_name}.zip")
    output_csv_path = os.path.join(source_dir, f"{zip_file_name}.csv")
    
    extract_and_save_csv(zip_file_path, output_csv_path)