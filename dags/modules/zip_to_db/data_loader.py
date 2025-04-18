# data_loader.py
#Stand: ungetestet 
#ist No 3 in works_v2

import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
import SQLAlchemy_functions as af


def load_and_process_data_from_csv(csv_file_path, session: Session, chunksize=100000, symbol_filter=None):
    total_rows = sum(1 for _ in open(csv_file_path)) - 1
    total_chunks = (total_rows // chunksize) + 1
    processed_chunks = 0

    for chunk in pd.read_csv(csv_file_path, chunksize=chunksize):
        processed_chunks += 1
        progress = (processed_chunks / total_chunks) * 100
        print(f"Verarbeite Chunk {processed_chunks}/{total_chunks} ({progress:.2f}%)")

        if 'date' not in chunk.columns or 'ticker' not in chunk.columns:
            raise ValueError("Die CSV-Datei muss die Spalten 'date' und 'ticker' enthalten.")

        chunk['date'] = pd.to_datetime(chunk['date'])
        chunk = chunk.set_index(['date', 'ticker']).sort_index()

        if symbol_filter:
            chunk = chunk.query(f'ticker == "{symbol_filter}"')

        chunk = (
            chunk.reset_index().set_index('date')
            .groupby('ticker').resample('1min').last().droplevel(0)
        )
        chunk.loc[:, chunk.columns[:-1]] = chunk[chunk.columns[:-1]].ffill()
        chunk['volume'] = chunk['volume'].fillna(0.0)
        chunk = chunk.reset_index().sort_values(by=['date', 'ticker']).set_index(['date', 'ticker'])

        tickers = chunk.index.get_level_values(1).unique()
        latest_date = chunk.index.get_level_values('date').max()
        active_tickers = chunk.loc[latest_date].index.get_level_values('ticker').unique()

        symbols = pd.DataFrame({'ticker': tickers, 'name': tickers, 'market': 'crypto'})
        symbols['active'] = symbols['ticker'].isin(active_tickers)

        try:
            # Dummy-Security: Du brauchst eine gültige security.sec_id, da es NOT NULL ist.
            # Das ist ein einfacher Default-Wert – in der Praxis solltest du evtl. security vorher aufbauen.
            default_security = session.query(af.Security).filter_by(exchange='default').first()
            if not default_security:
                default_security = af.Security(exchange='default', category='uncategorized', sector='unknown')
                session.add(default_security)
                session.flush()

            for r in symbols.itertuples():
                symbol = af.Symbol(
                    ticker=r.ticker,
                    name=r.name,
                    market=af.Market[r.market],
                    active=r.active,
                    sec_id=default_security.sec_id
                )
                session.add(symbol)
                session.flush()  # Holt die generierte sy_id

                if r.ticker in chunk.index.get_level_values('ticker'):
                    bars = chunk.xs(r.ticker, level='ticker').reset_index()
                    bars['sy_id'] = symbol.sy_id
                    bars = bars.rename(columns={
                        'open': 'open',
                        'high': 'high',
                        'low': 'low',
                        'close': 'close',
                        'volume': 'volume',
                        'date': 'date'
                    })
                    records = bars[['date', 'open', 'high', 'low', 'close', 'volume', 'sy_id']].to_dict(orient='records')
                    session.bulk_insert_mappings(af.MinuteBar, records)

            session.commit()

        except Exception as e:
            print(f"Fehler beim Hochladen von Symbolen: {e}")
            session.rollback()


#alte Funktionen die ggf falsch implementiert wurden:
'''
# No. 3 Funkton zum Laden und Verarbeiten von CSV-Dateien in die Datenbank

#Stand: Unbekannt

from modules.data_loader import load_and_process_data_from_csv

def load_and_process_data_from_csv(csv_file_path, session, chunksize=100000, symbol_filter=None):
    # Berechnen Sie die Gesamtzahl der Chunks
    
    print("pause")
    total_rows = sum(1 for _ in open(csv_file_path)) - 1  # Minus 1 für die Header-Zeile
    print(total_rows)
    total_chunks = (total_rows // chunksize) + 1
    print(total_chunks)
    
    # Initialisieren Sie den Zähler für die verarbeiteten Chunks
    processed_chunks = 0
    
    # Laden Sie die CSV-Datei in Chunks
    for chunk in pd.read_csv(csv_file_path, chunksize=chunksize):
        processed_chunks += 1
        progress = (processed_chunks / total_chunks) * 100
        print(f"Verarbeite Chunk {processed_chunks}/{total_chunks} ({progress:.2f}%)")
        
        # Überprüfen Sie, ob die erforderlichen Spalten vorhanden sind
        if 'date' not in chunk.columns or 'ticker' not in chunk.columns:
            print("CSV-Datei geladen. Erste Zeilen:")
            print(chunk.head())
            raise ValueError("Die CSV-Datei muss die Spalten 'date' und 'ticker' enthalten.")
        
        # Konvertieren des Datums und Setzen des Index
        chunk['date'] = pd.to_datetime(chunk['date'])
        chunk = chunk.set_index(['date', 'ticker'])
        chunk = chunk.sort_index()
        
        # Optional: Filter für ein bestimmtes Symbol setzen
        if symbol_filter:
            chunk = chunk.query(f'ticker == "{symbol_filter}"')
        
        # Resample auf 1-Minuten-Intervalle
        chunk = chunk.reset_index().set_index('date').groupby('ticker').resample('1min').last().droplevel(0)
        chunk.loc[:, chunk.columns[:-1]] = chunk[chunk.columns[:-1]].ffill()
        chunk.loc[:, 'volume'] = chunk['volume'].fillna(value=0.0)
        chunk = chunk.reset_index().sort_values(by=['date', 'ticker']).set_index(['date', 'ticker'])
        
        tickers = chunk.index.get_level_values(1).unique()
        latest_date = chunk.index.get_level_values('date').max()
        active_tickers = chunk.loc[latest_date].index.get_level_values('ticker').unique()
        
        symbols = pd.DataFrame(tickers, columns=['ticker'])
        symbols['name'] = symbols['ticker']
        symbols['market'] = 'crypto'
        symbols['active'] = np.where(symbols['ticker'].isin(active_tickers), True, False)
        symbols = symbols.sort_values(by='ticker')
        
        total_symbols = len(symbols)
        try:
            for i, r in enumerate(symbols.itertuples(), 1):
                symbol = af.Symbol(ticker=r.ticker, name=r.name, market=af.Market[r.market], active=r.active)
                session.add(symbol)
                
                # Überprüfen, ob der Index existiert
                if r.ticker in chunk.index.get_level_values('ticker'):
                    bars = chunk.xs(r.ticker, level='ticker').reset_index()
                    bars['symbol_id'] = symbol.id
                    
                    session.bulk_insert_mappings(af.MinuteBar, bars.to_dict(orient='records'))
            
            # Commit nach dem Verarbeiten des gesamten Chunks
            session.commit()
        except Exception as e:
            print(f"An error occurred while uploading symbols: {e}")
            session.rollback()'''