# Grabber_dag.py
#Stand: TODO ungetestet und noch zu überprüfen
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from modules.SQLAlchemy_functions import start_session
import pandas as pd
from modules.Grabber.grabber_load import process_asset

csv_file_path = './ref_assets.csv' # soll im gleichen Verzeichnis wie der dag gespeichert werden
config_file = './config.json'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 1),
    'retries': 1,
}

# erster Task
def check_csv(file_path):
    try:
        assets_df = pd.read_csv(file_path)
        with open(file_path, 'r') as file:
            content = file.read()
            if not content.strip():
                print("Die CSV-Datei ist leer.")
                return
    except Exception as e:
        print(f"Fehler beim Einlesen der CSV-Datei: {e}")
    return
    
# Haupttask in einer Schleife:
def load_and_process_assets(config_file, csv_file_path):
    session = start_session(config_file)
    assets_df = pd.read_csv(csv_file_path)
    for _, row in assets_df.iterrows():
        try:
            print("****************************************")
            process_asset(session, row)
        except Exception as e:
            print(f"Fehler beim Verarbeiten des Assets {row['ticker']}: {e}")
        continue  # Fortfahren mit dem nächsten Asset
    session.close()

with DAG('Grabber', default_args=default_args, schedule_interval='@daily') as dag:
    check_csv_task = PythonOperator(
        task_id='check_csv',
        python_callable=check_csv,
        op_args=[csv_file_path]
    )

    load_assets_task = PythonOperator(
        task_id='load_and_process_assets',
        python_callable=load_and_process_assets,
        op_args=[config_file, csv_file_path]
    )

    check_csv_task >> load_assets_task