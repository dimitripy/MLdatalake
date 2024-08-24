from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

def create_update_db():
    # Führen Sie hier die entsprechenden Skripte aus
    # z.B. subprocess.run(['python3', 'create_database.py'])
    pass

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 8, 1),
}

dag = DAG('create_update_db', default_args=default_args, schedule_interval='@daily')

t1 = PythonOperator(
    task_id='create_update_db_task',
    python_callable=create_update_db,
    dag=dag,
)
