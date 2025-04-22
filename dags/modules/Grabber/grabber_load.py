import pandas as pd
from datetime import datetime

import modules.SQLAlchemy_functions as af
from Asset_src.YahooFinance import load_yf_data

# CSV-Datei Pfad
csv_file_path = 'ref_assets.csv'


def check_if_asset_exists(session, row):
    # Prüfe, ob das Asset in der Datenbank existiert
    asset = session.query(af.Symbol).filter_by(ticker=row['ticker']).first()

    if asset:
        print(f"Asset {row['ticker']} existiert bereits. Überprüfe das letzte Update.")
        
        # Letztes Update des Assets prüfen und aktualisieren
        last_update = update_asset_last_update(session, row)
        
        if last_update:
            old = row['last_update']
            # Aktualisiere `row['last_update']` mit dem neuen Wert
            row['last_update'] = last_update
            print("Vorheriges last_update in row: ", old ," und Neues last_update in row:", row['last_update'])
            
            try:
                # Speichern in der Datenbank, wenn nötig
                asset.last_update = last_update  # Setze das letzte Update-Datum im Asset
                session.commit()  # Änderungen in der Datenbank speichern
                print(f"Asset {row['ticker']} erfolgreich aktualisiert mit letztem Update: {last_update}.")
            except Exception as e:
                session.rollback()  # Bei Fehlern Rollback durchführen
                print(f"Fehler beim Speichern des Updates für Asset {row['ticker']}: {e}")
        else:
            print(f"Kein Update für {row['ticker']} erforderlich.")
    else:
        print(f"Asset {row['ticker']} existiert nicht, füge es hinzu.")
        asset = add_new_asset(session, row)
    
    # Gib die aktualisierte `row` zurück
    return asset, row

"""
# Neues Asset hinzufügen
def add_new_asset(session, row):
    try:
        asset = af.Symbol(
            ticker=row['ticker'],
            name=row['name'],
            market=row['market'],
            active=row['active']
        )
        session.add(asset)
        session.commit()
        print(f"Asset {row['ticker']} erfolgreich hinzugefügt.")
    except Exception as e:
        print(f"Fehler beim Hinzufügen des Assets {row['ticker']}: {e}")
"""       
def add_new_asset(session, row):
    try:
        # Erstelle ein neues Asset mit den gegebenen Informationen
        asset = af.Symbol(
            ticker=row['ticker'],
            name=row['name'],
            market=row['market'],
            active=row['active'],
            start_date=datetime.now()  # Setze das Startdatum auf das aktuelle Datum
        )
        session.add(asset)
        session.commit()  # Sicherstellen, dass das Asset hinzugefügt wurde
        print(f"Asset {row['ticker']} erfolgreich hinzugefügt.")

        # Aktualisiere die CSV-Datei mit dem neuen Startdatum
        update_csv_start_date(csv_file_path, row['ticker'], asset.start_date)
        
        return asset
    except Exception as e:
        session.rollback()
        print(f"Fehler beim Hinzufügen des Assets {row['ticker']}: {e}")
        return None


# Aktualisieren der letzten Daten in der Asset-Tabelle
def update_asset_last_update(session, row):
    try:
        # Abfrage des Assets anhand des Tickers, um sicherzustellen, dass die Symbol-ID stimmt
        asset = session.query(af.Symbol).filter_by(ticker=row['ticker']).first()
        #print(f"Symbol-ID für {row['ticker']}: {asset.id}")
        
        # Überprüfen, welcher Zeitrahmen vorliegt
        if row['timeframe'] == '5m':
            last_update = session.query(af.FiveMinuteBar).filter_by(symbol_id=asset.id).order_by(af.FiveMinuteBar.date.desc()).first()
        elif row['timeframe'] == '30m':
            last_update = session.query(af.ThirtyMinuteBar).filter_by(symbol_id=asset.id).order_by(af.ThirtyMinuteBar.date.desc()).first()
        elif row['timeframe'] == '1m':  # 1-Minuten-Daten
            last_update = session.query(af.MinuteBar).filter_by(symbol_id=asset.id).order_by(af.MinuteBar.date.desc()).first()

        # Falls ein Update existiert, Datum zurückgeben
        if last_update:
            print(f"Symbol-ID für {row['ticker']}: {asset.id}. Letztes Update war am {last_update.date}")
            return last_update.date
        else:
            print(f"Kein letzter Eintrag für {row['ticker']} im Zeitrahmen {row['timeframe']} gefunden.")
            return None
    except Exception as e:
        session.rollback()
        print(f"Fehler beim Abrufen des letzten Updates für {row['ticker']}: {e}")
        return None

def update_csv_start_date(file_path, ticker, start_date):
    try:
        # Lesen der CSV-Datei
        df = pd.read_csv(file_path)
        
        # Aktualisieren des Startdatums für das Asset
        df.loc[df['ticker'] == ticker, 'start_date'] = start_date.strftime('%Y-%m-%d')
        
        # Speichern der aktualisierten CSV-Datei
        df.to_csv(file_path, index=False)
        print(f"Startdatum für Asset {ticker} in der CSV-Datei aktualisiert.")
    except Exception as e:
        print(f"Fehler beim Aktualisieren der CSV-Datei: {e}")
        
def update_csv_last_update(session, row, csv_file_path):
    last_update = update_asset_last_update(session, row)
    if last_update:
        # Lade die CSV-Datei
        df = pd.read_csv(csv_file_path)
        
        # Finde den entsprechenden Eintrag in der CSV und aktualisiere das Last-Update-Feld
        df.loc[df['ticker'] == row['ticker'], 'last_update'] = last_update
        
        # Schreibe die CSV-Datei zurück
        df.to_csv(csv_file_path, index=False)
        print(f"CSV-Datei für {row['ticker']} aktualisiert mit neuem Last Update: {last_update}")
    else:
        print(f"Kein Last Update für {row['ticker']} gefunden, CSV wurde nicht aktualisiert.")
        
        
# Dummy-Funktionen für verschiedene Exchanges
def process_binance_asset(session, row):
    print("Binance ist noch nicht implementiert.")
    #TODO Binance Option implementieren
    #print(f"Verarbeite Binance Asset: {row['ticker']}")

def process_yahoof_asset(session, row):
    asset, row = check_if_asset_exists(session, row)
    
    data = load_yf_data(row)
    
    if data:    
        print(f"Verarbeite Yahoo Finance Asset: {row['ticker']}")
        if row['timeframe'] == '1m':
            af.insert_data(session, data, af.MinuteBar, asset.id)
        elif row['timeframe'] == '5m':
            af.insert_data(session, data, af.FiveMinuteBar, asset.id)
        elif row['timeframe'] == '30m':
            af.insert_data(session, data, af.ThirtyMinuteBar, asset.id)
        else:
            print(f"Zeitrahmen {row['timeframe']} wird nicht unterstützt.")
            return
        update_csv_last_update(session, row, csv_file_path)
    
exchange_function_map = {
    'Binance': process_binance_asset,
    'Yahoo Finance': process_yahoof_asset
}

# Asset-Verarbeitung (Erstellen oder Aktualisieren)
def process_asset(session, row):

    # Verarbeiten des Assets basierend auf dem Exchange
    exchange = row['exchange']
    if exchange in exchange_function_map:
        exchange_function_map[exchange](session, row)
    else:
        print(f"Unbekannter Exchange: {exchange}")
