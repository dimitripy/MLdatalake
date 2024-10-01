from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import os
import sys
import json
import yaml
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Pfad zur Registry-Datei
REGISTRY_FILE = '/etc/airflow/airflow_dag_registry.yaml'


# Lade die Registry-Datei und extrahiere den Pfad zu den Modulen
def load_registry():
    if not os.path.exists(REGISTRY_FILE):
        raise FileNotFoundError(f"Registry-Datei nicht gefunden: {REGISTRY_FILE}")
    
    with open(REGISTRY_FILE, 'r') as file:
        registry = yaml.safe_load(file) or {}
    return registry

registry = load_registry()
DAG_PATH = registry['projects']['mldatalake']['dag_path']

# Fügen Sie den Pfad zu den Modulen hinzu

from create_database import Symbol, Market, MinuteBar

# Standardargumente für den DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Pfade zu den Skripten und Dateien
CONFIG_FILE = DAG_PATH +'/latest/config.json'
SOURCE_DIR = os.path.join(DAG_PATH, 'source')
ZIP_FILE_NAME = 'trimmed_file'
ZIP_FILE_PATH = os.path.join(SOURCE_DIR, f"{ZIP_FILE_NAME}.zip")
OUTPUT_CSV_PATH = os.path.join(SOURCE_DIR, f"{ZIP_FILE_NAME}.csv")

# Lade die Konfigurationsdatei
def load_config(config_file_path):
    with open(config_file_path, 'r') as file:
        config = json.load(file)
    return config

# Verbindungsschema für MySQL
def create_db_engine(config):
    db_type = "mysql+pymysql"
    url = f"{db_type}://{config['db_user']}:{config['db_password']}@{config['db_host']}:{config['db_port']}/{config['db_name']}"
    return create_engine(url, echo=False)

# Lade die Daten aus der CSV-Datei
def load_data_from_csv(csv_file_path):
    bars1m = pd.read_csv(csv_file_path, index_col=['date', 'ticker'])
    bars1m.index = pd.to_datetime(bars1m.index.get_level_values('date'))
    bars1m = bars1m.sort_values(by=['date', 'ticker'])
    return bars1m

# Verarbeite und füge die Daten in die Datenbank ein
def process_and_insert_data(session, bars1m, symbol_filter=None):
    if symbol_filter:
        bars1m = bars1m.query(f'ticker == "{symbol_filter}"')
    
    # Resample auf 1-Minuten-Intervalle
    bars1m = bars1m.reset_index().set_index('date').groupby('ticker').resample('1min').last().droplevel(0)
    bars1m.loc[:, bars1m.columns[:-1]] = bars1m[bars1m.columns[:-1]].ffill()
    bars1m.loc[:, 'volume'] = bars1m['volume'].fillna(value=0.0)
    bars1m = bars1m.reset_index().sort_values(by=['date', 'ticker']).set_index(['date', 'ticker'])
    
    tickers = bars1m.index.get_level_values(1).unique()
    latest_date = bars1m.index.get_level_values('date').max()
    active_tickers = bars1m.loc[latest_date].index.get_level_values('ticker').unique()
    
    symbols = pd.DataFrame(tickers, columns=['ticker'])
    symbols['name'] = symbols['ticker']
    symbols['market'] = 'crypto'
    symbols['active'] = np.where(symbols['ticker'].isin(active_tickers), True, False)
    symbols = symbols.sort_values(by='ticker')
    
    total_symbols = len(symbols)
    for i, r in symbols.iterrows():
        print(f"Uploading symbol {i+1}/{total_symbols}: {r['ticker']}")
        
        symbol = Symbol(ticker=r['ticker'], name=r['name'], market=Market[r['market']], active=r['active'])
        session.add(symbol)
        session.commit()
        
        bars = bars1m.xs(r['ticker']).reset_index()
        bars['symbol_id'] = symbol.id
        
        session.bulk_insert_mappings(MinuteBar, bars.to_dict(orient='records'))
        session.commit()

# Hauptfunktion zum Importieren der Daten
def import_data():
    try:
        # Einlesen der Konfigurationsdatei
        config = load_config(CONFIG_FILE)
        
        # Erstellen der Datenbank-Engine
        engine = create_db_engine(config)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Laden der Daten aus der CSV-Datei
        bars1m = load_data_from_csv(OUTPUT_CSV_PATH)
        
        # Optional: Filter für ein bestimmtes Symbol setzen
        symbol_filter = None  # Beispiel: Nur Daten für BTCUSD importieren, setze symbol_filter = "btcusd"
        process_and_insert_data(session, bars1m, symbol_filter)

        print("Data imported successfully")
    except Exception as e:
        print(f"An error occurred: {e}")

# Definition des DAGs
with DAG(
    'import_data_dag',
    default_args=default_args,
    description='Ein DAG zum Importieren von Daten in die Datenbank',
    schedule_interval=timedelta(days=1),
    catchup=False,
    max_active_runs=1,  
    tags=['PUT DB'],
) as dag:

    # Task zum Extrahieren der Daten aus der ZIP-Datei und Speichern in einer CSV-Datei
    extract_and_save_csv = BashOperator(
        task_id='extract_and_save_csv',
        bash_command=f'python {DAG_PATH}/latest/extract_and_save_csv.py'
    )

    # Task zum Importieren der Daten in die Datenbank
    import_data_task = PythonOperator(
        task_id='import_data',
        python_callable=import_data
    )

    # Task-Abhängigkeiten definieren
    extract_and_save_csv >> import_data_task