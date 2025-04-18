import zipfile
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import os
import json
import logging
import sys

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 1. Konfigurationsdaten aus JSON-Datei laden
def load_config(config_file_path):
    try:
        with open(config_file_path, 'r') as config_file:
            config = json.load(config_file)
        logging.info("Konfigurationsdaten erfolgreich geladen.")
        return config
    except Exception as e:
        logging.error(f"Fehler beim Laden der Konfigurationsdaten: {e}")
        raise

# 2. Zip-Datei entpacken
def unzip_file(zip_file_path, extract_to_path):
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to_path)
        logging.info("Zip-Datei erfolgreich entpackt.")
    except Exception as e:
        logging.error(f"Fehler beim Entpacken der Zip-Datei: {e}")
        raise

# NEUER ABSCHNITT: Symbol-Paare in separate CSV-Dateien trennen
def split_csv_by_symbol(extract_dir, output_directory):
    try:
        logging.info(f"Beginne mit der Trennung der Symbol-Paare in separate CSV-Dateien im Verzeichnis: {extract_dir}")
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith('.csv'):
                    file_path = os.path.join(root, file)
                    logging.info(f"Verarbeite CSV-Datei: {file_path}")
                    
                    # CSV-Datei laden
                    df = pd.read_csv(file_path)
                    
                    # Daten nach Symbol-Paaren gruppieren
                    grouped = df.groupby('symbol_pair')
                    
                    # Daten für jedes Symbol-Paar in separate CSV-Dateien speichern
                    for symbol_pair, group in grouped:
                        output_file = os.path.join(output_directory, f'{symbol_pair}.csv')
                        group.to_csv(output_file, index=False)
                        logging.info(f"Daten für Symbol-Paar {symbol_pair} gespeichert in {output_file}")
    except Exception as e:
        logging.error(f"Fehler bei der Trennung der Symbol-Paare: {e}")
        raise

# 3. Verarbeitung jeder CSV-Datei einzeln
def process_csv_files(extract_dir, db_path):
    try:
        logging.info(f"Beginne mit der Verarbeitung der CSV-Dateien im Verzeichnis: {extract_dir}")
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith('.csv'):
                    file_path = os.path.join(root, file)
                    logging.info(f"Verarbeite CSV-Datei: {file_path}")
                    process_single_csv(file_path, db_path)
    except Exception as e:
        logging.exception("Fehler bei der Verarbeitung der CSV-Dateien:")
        raise e

def process_single_csv(file_path, db_path):
    import sqlite3

    try:
        logging.info(f"Beginne mit der Verarbeitung der Datei: {file_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # CSV-Datei laden
        df = pd.read_csv(file_path)

        # Daten in die SQLite-Datenbank einfügen
        for index, row in df.iterrows():
            cursor.execute('''
                INSERT INTO minute_bar (date, open, high, low, close, volume, symbol_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (row['date'], row['open'], row['high'], row['low'], row['close'], row['volume'], row['symbol_id']))

        conn.commit()
        conn.close()
        logging.info(f"Verarbeitung der Datei {file_path} abgeschlossen und Datenbank aktualisiert.")
    except Exception as e:
        logging.exception(f"Fehler bei der Verarbeitung der Datei {file_path}:")
        raise e

# 4. Daten in MySQL-Datenbank laden
def load_data_to_db(db_path, db_user, db_password, db_host, db_name, table_name):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM minute_bar", conn)
        conn.close()

        engine = create_engine(f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}')
        df.to_sql(table_name, con=engine, if_exists='replace', index=False)
        logging.info("Daten erfolgreich in die MySQL-Datenbank geladen.")
    except Exception as e:
        logging.error(f"Fehler beim Laden der Daten in die MySQL-Datenbank: {e}")
        raise

# Hauptfunktion
def main(step):
    config_file_path = '/path/to/config.json'
    config = load_config(config_file_path)
    
    zip_file_path = config['zip_file_path']
    extract_to_path = config['extract_to_path']
    output_directory = config['output_directory']
    db_path = config['db_path']
    db_user = config['db_user']
    db_password = config['db_password']
    db_host = config['db_host']
    db_name = config['db_name']
    table_name = config['table_name']
    
    try:
        if step == 'unzip_file':
            unzip_file(zip_file_path, extract_to_path)
        elif step == 'split_csv':
            split_csv_by_symbol(extract_to_path, output_directory)
        elif step == 'process_data':
            process_csv_files(output_directory, db_path)
        elif step == 'load_data':
            load_data_to_db(db_path, db_user, db_password, db_host, db_name, table_name)
        else:
            logging.error(f"Unbekannter Schritt: {step}")
            return {"status": "error", "message": f"Unbekannter Schritt: {step}"}
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Fehler bei Schritt '{step}': {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else 'unzip_file'
    result = main(step)
    print(result)