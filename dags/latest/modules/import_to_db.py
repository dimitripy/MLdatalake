#import_to_db.py
import os
import json
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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

def main(config_file_path):
    try:
        config = load_config(config_file_path)
        engine = create_db_engine(config)
        Session = sessionmaker(bind=engine)
        session = Session()

        csv_file_path = './gespeicherter_dataframe.csv'
        bars1m = load_data_from_csv(csv_file_path)
        
        # Optional: Filter für ein bestimmtes Symbol setzen
        symbol_filter = None  # Beispiel: Nur Daten für BTCUSD importieren, setze symbol_filter = "btcusd"
        process_and_insert_data(session, bars1m, symbol_filter)

        print("Data imported successfully")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python import_to_db.py <config_file_path>")
        sys.exit(1)
    main(sys.argv[1])