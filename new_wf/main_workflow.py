from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import os
import requests
import json
import subprocess


# Konfigurationsdaten aus JSON-Datei laden
config_file_path = '/config.json'  # Pfad zur Konfigurationsdatei

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
    'db_backup_colab_workflow',
    default_args=default_args,
    description='Ein DAG zur Sicherung der Datenbank und zur Ausführung von Google Colab Tasks',
    schedule_interval=None,
    start_date=days_ago(1),
)

# Verbindung zur Datenbank testen
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

# Datenbank-Backup erstellen
def create_db_backup():
    backup_dir = "/path/to/backup"  # Backup-Verzeichnis
    backup_file = os.path.join(backup_dir, 'db_backup.sql')
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    command = f"mysqldump -u {db_user} -p{db_password} -h {db_host} {db_name} > {backup_file}"
    subprocess.run(command, shell=True, check=True)
    print(f"Datenbank-Backup gespeichert unter: {backup_file}")
    return backup_file

# Colab-Notebook-Schritt ausführen
def trigger_colab_notebook(step):
    response = requests.post(f"{colab_url}/trigger", json={"step": step})
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'success':
            print(f"Colab-Schritt '{step}' erfolgreich ausgeführt.")
        else:
            raise Exception(f"Fehler beim Ausführen des Schritts '{step}': {result.get('message')}")
    else:
        raise Exception(f"Fehler beim Starten des Schritts '{step}': {response.status_code}")

# Aufgaben in Airflow definieren
check_db_task = PythonOperator(
    task_id='check_db_connection',
    python_callable=check_db_connection,
    dag=dag,
)

create_backup_task = PythonOperator(
    task_id='create_db_backup',
    python_callable=create_db_backup,
    dag=dag,
)

trigger_colab_task = PythonOperator(
    task_id='trigger_colab_task',
    python_callable=lambda: trigger_colab_notebook('process_data'),
    dag=dag,
)

# Task-Reihenfolge definieren
check_db_task >> create_backup_task >> trigger_colab_task
