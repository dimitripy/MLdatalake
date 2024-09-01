# dag_fetch_save_parquet.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import subprocess

def fetch_save_parquet():
    subprocess.run(['python3', '/path/to/fetch_data.py'])
    subprocess.run(['python3', '/path/to/save_as_parquet.py'])

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 8, 1),
}

dag = DAG('fetch_save_parquet', default_args=default_args, schedule_interval='@daily')

t1 = PythonOperator(
    task_id='fetch_save_parquet_task',
    python_callable=fetch_save_parquet,
    dag=dag,
)
