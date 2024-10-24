# TODO Stand: Unbekannt 

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import os
import subprocess
import yaml
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'backup_dag',
    default_args=default_args,
    description='A DAG to backup the database and upload to Google Drive',
    schedule_interval=timedelta(days=1),
)

REGISTRY_FILE = '/etc/airflow/airflow_dag_registry.yaml'

def load_registry_file():
    with open(REGISTRY_FILE, 'r') as file:
        registry = yaml.safe_load(file)
    return registry

def create_db_backup():
    registry = load_registry_file()
    backup_dir = registry['mldatalake']['backup_dir']
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    backup_file = os.path.join(backup_dir, 'db_backup.sql')
    command = f"mysqldump -u root -p{os.getenv('MYSQL_PASSWORD')} -h localhost -P 3308 mldatalake > {backup_file}"
    subprocess.run(command, shell=True, check=True)
    return backup_file

def upload_to_gdrive(backup_file):
    registry = load_registry_file()
    api_key_file = registry['mldatalake']['api_key_file']
    
    # API-Schlüssel aus der Datei lesen
    with open(api_key_file, 'r') as file:
        api_key = file.read().strip()
    
    service = build('drive', 'v3', developerKey=api_key)

    file_metadata = {'name': 'db_backup.sql'}
    media = MediaFileUpload(backup_file, mimetype='application/sql')

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f"File ID: {file.get('id')}")

create_backup_task = PythonOperator(
    task_id='create_db_backup',
    python_callable=create_db_backup,
    dag=dag,
)

upload_backup_task = PythonOperator(
    task_id='upload_to_gdrive',
    python_callable=upload_to_gdrive,
    op_args=['{{ task_instance.xcom_pull(task_ids="create_db_backup") }}'],
    dag=dag,
)

create_backup_task >> upload_backup_task