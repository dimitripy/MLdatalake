#dag_update_db.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import subprocess

# Pfade definieren
zip_file_path = '/path/to/archive.zip'
extract_dir = '/path/to/extracted/'
db_path = '/content/drive/MyDrive/crypto_data.db'

# Datenbank erstellen und aktualisieren
def create_update_db():
    subprocess.run(['python3', '/path/to/create_database.py'])

# Überprüfen, ob die Zip-Datei entpackt ist
def check_unzip(**kwargs):
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)
        return 'unzip_task'
    else:
        # Wenn die Dateien bereits entpackt sind, überspringen
        return 'process_csv_files'

# Entpacken der Zip-Datei
def unzip(**kwargs):
    subprocess.run(['unzip', '-o', zip_file_path, '-d', extract_dir])

# Verarbeitung jeder CSV-Datei einzeln
def process_csv_files(**kwargs):
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                process_single_csv(file_path)

def process_single_csv(file_path):
    import sqlite3
    import pandas as pd

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # CSV-Datei laden
    df = pd.read_csv(file_path)

    # Daten in die SQLite-Datenbank einfügen
    for index, row in df.iterrows():
        cursor.execute('''
            INSERT INTO minute_bar (date, open, high, low, close, volume, symbol_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (row['date'], row['open'], row['high'], row['low'], row['close'], row['volume'], row['symbol_id']))

    conn.commit()
    conn.close()

# Airflow DAG Definition
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 8, 1),
}

dag = DAG('update_db_from_zip', default_args=default_args, schedule_interval='@daily')

# Tasks definieren
create_update_db_task = PythonOperator(
    task_id='create_update_db_task',
    python_callable=create_update_db,
    dag=dag,
)

check_unzip_task = PythonOperator(
    task_id='check_unzip',
    python_callable=check_unzip,
    provide_context=True,
    dag=dag,
)

unzip_task = PythonOperator(
    task_id='unzip_task',
    python_callable=unzip,
    dag=dag,
)

process_csv_task = PythonOperator(
    task_id='process_csv_files',
    python_callable=process_csv_files,
    dag=dag,
)

# Task-Abhängigkeiten definieren
create_update_db_task >> check_unzip_task >> unzip_task >> process_csv_task
check_unzip_task >> process_csv_task
