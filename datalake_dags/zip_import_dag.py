from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import os
import pandas as pd
import zipfile
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from create_database import Symbol, Market

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
    'import_data_dag',
    default_args=default_args,
    description='A simple data import DAG',
    schedule_interval=timedelta(days=1),
)

REGISTRY_FILE = '/etc/airflow/airflow_dag_registry.yaml'

def load_registry_file():
    with open(REGISTRY_FILE, 'r') as file:
        registry = yaml.safe_load(file)
    return registry

def load_env_variables():
    load_dotenv()
    return {
        'mysql_host': os.getenv('MYSQL_HOST', 'localhost'),
        'mysql_user': os.getenv('MYSQL_USER', 'root'),
        'mysql_password': os.getenv('MYSQL_PASSWORD', 'root'),
        'mysql_database': os.getenv('MYSQL_DATABASE', 'mydatabase'),
        'mysql_port': int(os.getenv('MYSQL_PORT', 3306))
    }

def create_db_engine(env_vars):
    db_type = "mysql+pymysql"
    url = f"{db_type}://{env_vars['mysql_user']}:{env_vars['mysql_password']}@{env_vars['mysql_host']}:{env_vars['mysql_port']}/{env_vars['mysql_database']}"
    return create_engine(url, echo=False)

def extract_zip(**kwargs):
    registry = load_registry_file()
    data_dir = registry['mldatalake']['data_dir']
    zip_file_path = os.path.join(data_dir, 'data.zip')
    extract_to = os.path.join(data_dir, 'extracted_data')
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def read_csv(**kwargs):
    registry = load_registry_file()
    data_dir = registry['mldatalake']['data_dir']
    csv_file_path = os.path.join(data_dir, 'extracted_data/data.csv')
    df = pd.read_csv(csv_file_path)
    return df

def process_data(**kwargs):
    ti = kwargs['ti']
    df = ti.xcom_pull(task_ids='read_csv')
    
    # Datenaufbereitung
    df = df.droplevel(1).reset_index().rename(columns={'index': 'ticker'})
    df = df[df['ticker'].str.contains('usd')]
    df['date'] = pd.to_datetime(df['time'], unit='ms')
    df = df.sort_values(by=['date', 'ticker'])
    df = df.drop(columns='time')
    df = df.set_index(['date', 'ticker'])
    # df = df['2021-07-01':'2021-12-31']
    
    df['active'] = df['active'].astype(bool)
    df['market'] = df['market'].apply(lambda x: x.upper())
    
    ti.xcom_push(key='processed_data', value=df)

def import_data_to_db(**kwargs):
    ti = kwargs['ti']
    df = ti.xcom_pull(task_ids='process_data', key='processed_data')
    env_vars = load_env_variables()
    engine = create_db_engine(env_vars)
    Session = sessionmaker(bind=engine)
    session = Session()
    for index, row in df.iterrows():
        symbol = Symbol(
            ticker=row['ticker'],
            name=row['name'],
            market=Market[row['market']],
            active=row['active']
        )
        session.add(symbol)
    session.commit()

extract_task = PythonOperator(
    task_id='extract_zip',
    python_callable=extract_zip,
    dag=dag,
)

read_task = PythonOperator(
    task_id='read_csv',
    python_callable=read_csv,
    dag=dag,
)

process_task = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    provide_context=True,
    dag=dag,
)

import_task = PythonOperator(
    task_id='import_data_to_db',
    python_callable=import_data_to_db,
    provide_context=True,
    dag=dag,
)

extract_task >> read_task >> process_task >> import_task