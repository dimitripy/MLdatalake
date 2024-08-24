from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

def fetch_save_parquet():
    # Führen Sie hier die entsprechenden Skripte aus
    # z.B. subprocess.run(['python3', 'fetch_data.py'])
    # subprocess.run(['python3', 'save_as_parquet.py'])
    pass

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
