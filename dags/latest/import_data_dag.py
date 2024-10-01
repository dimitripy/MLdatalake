from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import sys
import os
import yaml  # Importieren des yaml-Moduls
import json
from airflow.utils.log.logging_mixin import LoggingMixin
import subprocess

# Verwende den Airflow-Logger
log = LoggingMixin().log

# Fügen Sie das Verzeichnis zum Python-Pfad hinzu
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
import create_database
import extract_and_save_csv
import import_to_db

# Überprüfen und installieren Sie pymysql, falls es nicht vorhanden ist
def ensure_pymysql_installed():
    try:
        import pymysql
        log.info("pymysql ist bereits installiert.")
    except ImportError:
        log.info("pymysql ist nicht installiert. Installation wird durchgeführt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pymysql"])
        log.info("pymysql wurde erfolgreich installiert.")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

dag = DAG(
    'upload_crypto_data',
    default_args=default_args,
    description='A simple crypto data pipeline',
    schedule_interval='@daily',
    catchup=False,  # Deaktiviert das Nachholen verpasster Ausführungen
    max_active_runs=1,  # Beschränkt die Anzahl der gleichzeitig aktiven DAG-Runs
    tags=['PUT DB'],
)

REGISTRY_FILE = '/etc/airflow/airflow_dag_registry.yaml'

def load_registry():
    if not os.path.exists(REGISTRY_FILE):
        log.error(f"Registry-Datei nicht gefunden: {REGISTRY_FILE}")
        return {}
    
    with open(REGISTRY_FILE, 'r') as file:
        registry = yaml.safe_load(file) or {}
    log.info("Registry erfolgreich geladen.")
    return registry

# Lade die Konfigurationsdatei
def load_config(config_file_path):
    if not os.path.exists(config_file_path):
        log.error(f"Konfigurationsdatei nicht gefunden: {config_file_path}")
        raise FileNotFoundError(f"Konfigurationsdatei nicht gefunden: {config_file_path}")
    
    with open(config_file_path, 'r') as file:
        config = json.load(file)
    log.info("Konfigurationsdatei erfolgreich geladen.")
    return config

config_file_path = os.path.join(os.path.dirname(__file__), 'config.json')
config = load_config(config_file_path)

def run_create_database(config_file_path):
    log.info("Starte Datenbankerstellung...")
    create_database.main(config_file_path)
    log.info("Datenbankerstellung abgeschlossen.")

def run_extract_and_save_csv():
    log.info("Starte Extraktion und Speicherung der CSV-Datei...")
    # Lesen Sie den Pfad zum source-Verzeichnis aus der Registry
    registry = load_registry()
    
    source_directory = registry.get('projects', {}).get('mldatalake', {}).get('source_path')
    
    if not source_directory:
        log.error("Source directory not found in registry")
        raise ValueError("Source directory not found in registry")

    # Laden Sie den Namen der ZIP-Datei aus der Konfigurationsdatei
    zip_file_name = config.get('zip_file_name')
    
    if not zip_file_name:
        log.error("ZIP file name not found in config")
        raise ValueError("ZIP file name not found in config")

    zip_file_path = os.path.join(source_directory, f"{zip_file_name}.zip")
    output_csv_path = os.path.join(source_directory, f"{zip_file_name}.csv")
    
    extract_and_save_csv.extract_and_save_csv(zip_file_path, output_csv_path)
    log.info("Extraktion und Speicherung der CSV-Datei abgeschlossen.")

def run_import_to_db(config_file_path):
    log.info("Starte Import in die Datenbank...")
    import_to_db.main(config_file_path)
    log.info("Import in die Datenbank abgeschlossen.")

ensure_pymysql_task = PythonOperator(
    task_id='ensure_pymysql_installed',
    python_callable=ensure_pymysql_installed,
    dag=dag,
)

create_db_task = PythonOperator(
    task_id='create_database',
    python_callable=run_create_database,
    op_args=[config_file_path],
    dag=dag,
)

extract_task = PythonOperator(
    task_id='extract_and_save_csv',
    python_callable=run_extract_and_save_csv,
    dag=dag,
)

import_task = PythonOperator(
    task_id='import_to_db',
    python_callable=run_import_to_db,
    op_args=[config_file_path],
    dag=dag,
)

ensure_pymysql_task >> create_db_task >> extract_task >> import_task