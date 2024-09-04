# dag_fetch_save_parquet.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import subprocess
from airflow.utils.log.logging_mixin import LoggingMixin

# Logger initialisieren
log = LoggingMixin().log

# Skriptpfade definieren
fetch_data_script = '/path/to/fetch_data.py'
save_parquet_script = '/path/to/save_as_parquet.py'

# Funktion zum Abrufen der Daten
def fetch_data():
    try:
        log.info(f"Starte das Abrufen der Daten mit {fetch_data_script}...")
        subprocess.run(['python3', fetch_data_script], check=True)
        log.info("Daten erfolgreich abgerufen.")
    except subprocess.CalledProcessError as e:
        log.error(f"Fehler beim Abrufen der Daten: {e}")
        raise e

# Funktion zum Speichern der Daten als Parquet
def save_as_parquet():
    try:
        log.info(f"Starte das Speichern der Daten als Parquet mit {save_parquet_script}...")
        subprocess.run(['python3', save_parquet_script], check=True)
        log.info("Daten erfolgreich als Parquet gespeichert.")
    except subprocess.CalledProcessError as e:
        log.error(f"Fehler beim Speichern als Parquet: {e}")
        raise e

# Airflow DAG Definition
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 8, 1),
}

dag = DAG('fetch_save_parquet', default_args=default_args, schedule_interval='@daily')

# Tasks definieren
fetch_data_task = PythonOperator(
    task_id='fetch_data_task',
    python_callable=fetch_data,
    dag=dag,
)

save_as_parquet_task = PythonOperator(
    task_id='save_as_parquet_task',
    python_callable=save_as_parquet,
    dag=dag,
)

# Task-Abhängigkeiten definieren
fetch_data_task >> save_as_parquet_task
