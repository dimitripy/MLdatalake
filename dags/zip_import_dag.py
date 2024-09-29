import os
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import mysql.connector
import requests
import json

# Konfigurationsdaten aus JSON-Datei laden
current_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(current_dir, 'config.json')

with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

db_user = config['db_user']
db_password = config['db_password']
db_host = config['db_host']
db_name = config['db_name']
colab_url = config['colab_url']

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

dag = DAG(
    'zip_import_for_coworker_dag',
    default_args=default_args,
    description='Ein DAG zum Starten eines Google Colab Notebooks zur Datenverarbeitung',
    schedule_interval=None,
    start_date=days_ago(1),
)

def check_db_connection():
    try:
        conn = mysql.connector.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            database=db_name
        )
        conn.close()
        print("Verbindung zur Datenbank erfolgreich.")
    except mysql.connector.Error as err:
        print(f"Fehler bei der Verbindung zur Datenbank: {err}")
        raise

def trigger_colab_notebook(step):
    response = requests.post(f"{colab_url}?step={step}")
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'success':
            print(f"Google Colab Notebook Schritt '{step}' erfolgreich ausgeführt.")
        else:
            raise Exception(f"Fehler beim Ausführen des Google Colab Notebooks Schritt '{step}': {result.get('message')}")
    else:
        raise Exception(f"Fehler beim Starten des Google Colab Notebooks Schritt '{step}': {response.status_code}")

check_db_task = PythonOperator(
    task_id='check_db_connection',
    python_callable=check_db_connection,
    dag=dag,
)

trigger_unzip_task = PythonOperator(
    task_id='trigger_unzip_file',
    python_callable=lambda: trigger_colab_notebook('unzip_file'),
    dag=dag,
)

trigger_split_csv_task = PythonOperator(
    task_id='trigger_split_csv',
    python_callable=lambda: trigger_colab_notebook('split_csv'),
    dag=dag,
)

trigger_process_data_task = PythonOperator(
    task_id='trigger_process_data',
    python_callable=lambda: trigger_colab_notebook('process_data'),
    dag=dag,
)

trigger_load_data_task = PythonOperator(
    task_id='trigger_load_data',
    python_callable=lambda: trigger_colab_notebook('load_data'),
    dag=dag,
)

check_db_task >> trigger_unzip_task >> trigger_split_csv_task >> trigger_process_data_task >> trigger_load_data_task