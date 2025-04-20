#Modul um das Zipfile in die datenbank in einem start hochzuladen.

import zipfile
import os
import json
import logging
import sys

from Uploader import DatabaseUploader
import pandas as pd
import logging


# 2. Zip-Datei entpacken
def unzip_file(zip_file_path, extract_to_path):
    try:
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(extract_to_path)
        logging.info("Zip-Datei erfolgreich entpackt.")
    except Exception as e:
        logging.error(f"Fehler beim Entpacken der Zip-Datei: {e}")
        raise


# NEUER ABSCHNITT: Symbol-Paare in separate CSV-Dateien trennen
def split_csv_by_symbol(extract_dir, output_directory):
    try:
        logging.info(
            f"Beginne mit der Trennung der Symbol-Paare in separate CSV-Dateien im Verzeichnis: {extract_dir}"
        )
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith(".csv"):
                    file_path = os.path.join(root, file)
                    logging.info(f"Verarbeite CSV-Datei: {file_path}")

                    # CSV-Datei laden
                    df = pd.read_csv(file_path)

                    # Daten nach Symbol-Paaren gruppieren
                    grouped = df.groupby("symbol_pair")

                    # Daten für jedes Symbol-Paar in separate CSV-Dateien speichern
                    for symbol_pair, group in grouped:
                        output_file = os.path.join(
                            output_directory, f"{symbol_pair}.csv"
                        )
                        group.to_csv(output_file, index=False)
                        logging.info(
                            f"Daten für Symbol-Paar {symbol_pair} gespeichert in {output_file}"
                        )
    except Exception as e:
        logging.error(f"Fehler bei der Trennung der Symbol-Paare: {e}")
        raise

def get_ticker(file_path):
    try:
        df = pd.read_csv(file_path, usecols=['ticker'])
        unique_tickers = df['ticker'].nunique()

        if unique_tickers == 1:
            return df['ticker'].iloc[0]
        elif unique_tickers == 0:
            logging.warning(f"Keine Ticker in Datei {file_path}.")
            return None
        else:
            logging.warning(f"Mehrere verschiedene Ticker in Datei {file_path}.")
            return None
    except Exception as e:
        logging.exception(f"Fehler beim Lesen der Datei {file_path}: {e}")
        return None

def validate_data(extract_dir, uploader, name, market, exchange, sector, categor):
    
    try:
        logging.info(
            f"Beginne mit der Überprüfung ob die Symbole vorhanden sind")
            
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith(".csv"):
                    file_path = os.path.join(root, file)
                    ticker = get_ticker(file_path)
                    uploader.add_symbol(ticker=ticker, name= None, market="crypto", exchange="Binance", sector="", category="CRYPTOCURRENCY")
    except Exception as e:
        logging.exception("Fehler bei der Verarbeitung der CSV-Dateien:")
        raise e
    


# 3. Verarbeitung jeder CSV-Datei einzeln
def upload_dir(extract_dir, uploader):
    try:
        logging.info(
            f"Beginne mit der Verarbeitung der CSV-Dateien im Verzeichnis: {extract_dir}"
        )
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith(".csv"):
                    file_path = os.path.join(root, file)
                    logging.info(f"Verarbeite CSV-Datei: {file_path}")
                    process_single_csv(file_path, uploader)
    except Exception as e:
        logging.exception("Fehler bei der Verarbeitung der CSV-Dateien:")
        raise e

def process_single_csv(file_path, uploader):

    try:
        logging.info(f"Beginne mit der Verarbeitung der Datei: {file_path}")

        # CSV-Datei laden
        df = pd.read_csv(file_path)
        upload_status = uploader.upload_data( df, table_name=table_name, source_name=source_name)

        if upload_status == "success":
            logging.info(
                f"Verarbeitung der Datei {file_path} abgeschlossen und Datenbank aktualisiert."
            )
        else: 
            raise e
        return upload_status
        
    except Exception as e:
        logging.exception(f"Fehler bei der Verarbeitung der Datei {file_path}:")
        raise e




# Hauptfunktion
def main(step, zip_file_path, extract_to_path, output_directory, config_pwd, table_name, source_name):

    uploader = DatabaseUploader(config_pwd)



    try:
        if step == "unzip_file":
            unzip_file(zip_file_path, extract_to_path)
        elif step == "split_csv":
            split_csv_by_symbol(extract_to_path, output_directory)
        elif step == "validate_data":
            validate_data(output_directory  ,name= None, market="crypto", exchange="Binance", sector= None, category="CRYPTOCURRENCY")
            #TODO Validate data + create new symbols
            pass
        elif step == "upload_data":
            upload_dir(output_directory, uploader)
        else:
            logging.error(f"Unbekannter Schritt: {step}")
            return {"status": "error", "message": f"Unbekannter Schritt: {step}"}
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Fehler bei Schritt '{step}': {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    zip_file_path = ""
    extract_to_path = ""
    output_directory = ""
    table_name="minute_bar"
    source_name="Yahoo Finance"

    config_pwd = (
        "/home/ageq/Git_Projects/MLdatalake/c_mldatalake/DataManager/config.json"
    )
    step = sys.argv[1] if len(sys.argv) > 1 else "unzip_file"
    result = main(
        step,
        zip_file_path=zip_file_path,
        extract_to_path=extract_to_path,
        output_directory=output_directory,
        config_pwd=config_pwd,
    )
    print(result)
