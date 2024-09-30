from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import create_database
import extract_and_save_csv
import import_to_db
import json

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

dag = DAG(
    'crypto_data_pipeline',
    default_args=default_args,
    description='A simple crypto data pipeline',
    schedule_interval='@daily',
)

# Lade die Konfigurationsdatei
def load_config(config_file_path):
    with open(config_file_path, 'r') as file:
        config = json.load(file)
    return config

config_file_path = '/path/to/config.json'
config = load_config(config_file_path)

def run_create_database(config_file_path):
    create_database.main(config_file_path)

def run_extract_and_save_csv():
    zip_file_path = '/path/to/archive.zip'
    output_csv_path = '/path/to/gespeicherter_dataframe.csv'
    extract_and_save_csv.extract_and_save_csv(zip_file_path, output_csv_path)

def run_import_to_db(config_file_path):
    import_to_db.main(config_file_path)

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

create_db_task >> extract_task >> import_task