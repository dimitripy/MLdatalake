#Stand: Unbekannt

import os
import sys
import json
import pandas as pd
import numpy as np
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Fügen Sie den Pfad zu `create_database.py` hinzu
sys.path.append('/opt/airflow/dags/mldatalake/latest/modules')

from create_database import Symbol, Market, MinuteBar

# Lade die Konfigurationsdatei
def load_config(config_file_path):
    with open(config_file_path, 'r') as file:
        config = json.load(file)
    return config

def create_db_engine(config):
    db_type = "mysql+pymysql"
    url = f"{db_type}://{config['db_user']}:{config['db_password']}@{config['db_host']}:{config['db_port']}/{config['db_name']}"
    return create_engine(url, echo=False)

def load_data_from_csv(csv_file_path):
    bars1m = pd.read_csv(csv_file_path, index_col=['date', 'ticker'])
    bars1m.index = pd.to_datetime(bars1m.index.get_level_values('date'))
    bars1m = bars1m.sort_values(by=['date', 'ticker'])
    return bars1m

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

def main():
    try:
        # Pfad zur config.json Datei
        config_path = '/opt/airflow/dags/mldatalake/latest/config.json'
        
        # Einlesen der Konfigurationsdatei
        config = load_config(config_path)
        
        # Pfad zur Registry-Datei
        registry_file_path = '/etc/airflow/airflow_dag_registry.yaml'
        
        # Einlesen der Registry-Datei
        with open(registry_file_path, 'r') as registry_file:
            registry = yaml.safe_load(registry_file)
        
        # Extrahieren des Pfades aus der Registry-Datei
        registry_path = registry['path_to_registry']
        
        # Erstellen des vollständigen Pfades zur ZIP-Datei
        zip_file_name = config['zip_file_name']
        output_csv_path = os.path.join(registry_path, f"{zip_file_name}.csv")
        
        # Erstellen der Datenbank-Engine
        engine = create_db_engine(config)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Laden der Daten aus der CSV-Datei
        bars1m = load_data_from_csv(output_csv_path)
        
        # Optional: Filter für ein bestimmtes Symbol setzen
        symbol_filter = None  # Beispiel: Nur Daten für BTCUSD importieren, setze symbol_filter = "btcusd"
        process_and_insert_data(session, bars1m, symbol_filter)

        print("Data imported successfully")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()