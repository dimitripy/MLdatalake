# zip_to_db_dag.py
#Stand: ungetetstet
# Verarbeitet die Module wie aus works_v2 von No. 1-3 in einem DAG
#TODO Testen
#zum Testen:in diesens File in den dags Ordner kopieren und in der Konsole "airflow dags test zip_to_db_dag 2023-01-01" eingeben

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from SQLAlchemy_functions import start_session
from data_loader import load_and_process_data_from_csv
from zip_extractor import main_extract_zip
from csv_converter import main_convert_csv

default_args = {
    'owner': 'airflow',
    'retries': 1,
}

config_path = './config.json'
source_path = '/home/ageq/Git_Projects/MLdatalake/source'
extract_to_path= source_path+'/archive'  #Muss gleich wie in der config.json sein
output_csv_path= source_path+'/combined.csv'


def run_data_loading():
    session = start_session(config_path)
    try:
        load_and_process_data_from_csv(
            csv_file_path=output_csv_path,
            session=session,
            chunksize=100000,
        )
    finally:
        session.close()

with DAG(
    dag_id='zip_to_db_dag',
    default_args=default_args,
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
) as dag:

    extract_task = PythonOperator(
        task_id='extract_zip',
        python_callable=main_extract_zip,
        op_kwargs={
            'config_path': config_path,
            'source_path': '/home/ageq/Git_Projects/MLdatalake/source'
        }
    )

    convert_csv_task = PythonOperator(
        task_id='convert_csv_files',
        python_callable=main_convert_csv,
        op_kwargs={
            'extract_to_path': extract_to_path,
            'output_csv_path': output_csv_path
        }
    )

    data_loading_task = PythonOperator(
        task_id='load_and_process_data',
        python_callable=run_data_loading
    )




    extract_task >> convert_csv_task >> data_loading_task
