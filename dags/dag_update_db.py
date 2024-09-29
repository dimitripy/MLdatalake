# dag_update_db.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import subprocess
from airflow.utils.log.logging_mixin import LoggingMixin

# Logger initialisieren
log = LoggingMixin().log

# Basisverzeichnis für das Projekt
base_path = '/opt/airflow/dags/MLdatalake'  # Basisverzeichnis im Container

# Fester Ordner für die ZIP-Datei und Extraktion
zipped_data_folder = os.path.join(base_path, 'zipped_data')
zip_file_path = os.path.join(zipped_data_folder, 'archive.zip')
extract_dir = os.path.join(zipped_data_folder, 'extracted')
db_path = '/content/drive/MyDrive/crypto_data.db'  # Pfad zur Datenbank

# Task zum Erstellen des festen Ordners und Ablegen der ZIP-Datei
def prepare_environment():
    try:
        if os.path.exists(zipped_data_folder):
            log.info(f"Bereinige das Zipped Data Verzeichnis: {zipped_data_folder}")
            subprocess.run(['rm', '-rf', zipped_data_folder], check=True)
        os.makedirs(extract_dir, exist_ok=True)
        log.info(f"Zipped Data Verzeichnis erstellt: {zipped_data_folder}")
    except Exception as e:
        log.exception("Fehler beim Vorbereiten des Verzeichnisses:")
        raise e

# Datenbank erstellen und aktualisieren
def create_update_db():
    try:
        log.info("Starte die Erstellung und Aktualisierung der Datenbank...")
        subprocess.run(['python3', os.path.join(base_path, 'create_database.py')], check=True)
        log.info("Datenbank erfolgreich erstellt und aktualisiert.")
    except subprocess.CalledProcessError as e:
        log.error("Fehler beim Erstellen der Datenbank:", exc_info=e)
        raise e

# Überprüfen, ob die ZIP-Datei entpackt ist
def check_unzip(**kwargs):
    try:
        log.info("Überprüfe, ob die ZIP-Datei entpackt ist...")
        if not os.path.exists(extract_dir) or not os.listdir(extract_dir):
            log.info("Extraktionsverzeichnis ist leer oder existiert nicht. Entpacken erforderlich.")
            return 'unzip_task'
        else:
            log.info("Extraktionsverzeichnis bereits vorhanden. Überspringe das Entpacken.")
            return 'process_csv_files'
    except Exception as e:
        log.exception("Fehler bei der Überprüfung des Extraktionsverzeichnisses:")
        raise e

# Entpacken der ZIP-Datei
def unzip(**kwargs):
    try:
        log.info(f"Entpacke die ZIP-Datei: {zip_file_path} in das Verzeichnis: {extract_dir}")
        subprocess.run(['unzip', '-o', zip_file_path, '-d', extract_dir], check=True)
        log.info("ZIP-Datei erfolgreich entpackt.")
    except subprocess.CalledProcessError as e:
        log.error("Fehler beim Entpacken der ZIP-Datei:", exc_info=e)
        raise e

# Verarbeitung jeder CSV-Datei einzeln
def process_csv_files(**kwargs):
    try:
        log.info(f"Beginne mit der Verarbeitung der CSV-Dateien im Verzeichnis: {extract_dir}")
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith('.csv'):
                    file_path = os.path.join(root, file)
                    log.info(f"Verarbeite CSV-Datei: {file_path}")
                    process_single_csv(file_path)
    except Exception as e:
        log.exception("Fehler bei der Verarbeitung der CSV-Dateien:")
        raise e

def process_single_csv(file_path):
    import sqlite3
    import pandas as pd

    try:
        log.info(f"Beginne mit der Verarbeitung der Datei: {file_path}")
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
        log.info(f"Verarbeitung der Datei {file_path} abgeschlossen und Datenbank aktualisiert.")
    except Exception as e:
        log.exception(f"Fehler bei der Verarbeitung der Datei {file_path}:")
        raise e

# Airflow DAG Definition
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 8, 1),
}

dag = DAG('update_db_from_zip', default_args=default_args, schedule_interval='@daily')

# Tasks definieren
prepare_environment_task = PythonOperator(
    task_id='prepare_environment_task',
    python_callable=prepare_environment,
    dag=dag,
)

create_update_db_task = PythonOperator(
    task_id='create_update_db_task',
    python_callable=create_update_db,
    dag=dag,
)

check_unzip_task = PythonOperator(
    task_id='check_unzip',
    python_callable=check_unzip,
    provide_context=True,
    dag=dag,
)

unzip_task = PythonOperator(
    task_id='unzip_task',
    python_callable=unzip,
    dag=dag,
)

process_csv_task = PythonOperator(
    task_id='process_csv_files',
    python_callable=process_csv_files,
    dag=dag,
)

# Task-Abhängigkeiten definieren
prepare_environment_task >> create_update_db_task >> check_unzip_task >> unzip_task >> process_csv_task
check_unzip_task >> process_csv_task
