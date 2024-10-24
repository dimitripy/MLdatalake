import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def load_yf_data(row):
    ticker = row['ticker']
    last_update = row['last_update']#.strip()  # Entferne führende/trailing Leerzeichen
    timeframe = row['timeframe']
    #print(f"Originaler last_update-Wert: '{last_update}'")  # Debugging
    
    # Überprüfen, ob last_update bereits ein datetime-Objekt ist
    if isinstance(last_update, str):
        try:
            # Datum ohne überflüssige Teile verarbeiten
            last_update = last_update.split(' ')[0]  # Nur das Datum übernehmen
            last_update_dt = datetime.strptime(last_update, '%Y-%m-%d')  # String in datetime umwandeln
        except ValueError as e:
            print(f"Fehler beim Parsen von last_update: {e}")  # Explizites Debugging bei Umwandlungsfehler
            return None
    elif isinstance(last_update, datetime):
        last_update_dt = last_update
    else:
        print(f"Unbekannter Typ für last_update: {type(last_update)}")
        return None
    
    # Starte den Abruf am nächsten Tag nach dem letzten Update
    start_date = last_update_dt + timedelta(days=1)
    
    # Bestimme das Enddatum als gestriger Tag
    end_date = datetime.now() - timedelta(days=1)

    # Falls das Startdatum zu weit in der Vergangenheit liegt, beschränke den Abruf auf maximal 59 Tage
    max_start_date = end_date - timedelta(days=58)
    if start_date < max_start_date:
        start_date = max_start_date

    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')

    # Überprüfen, ob bei der Abfrage mindestens ein Tag dazwischen liegt
    if (end_date - start_date).days < 1:
        print(f"Asset {row['ticker']} wurde kürzlich aktualisiert. Überspringe Verarbeitung.")
        return None
    
    print(f"Abruf von Daten für {ticker} von {start_str} bis {end_str}")  # Debugging für den Abrufzeitraum

    # Abrufen der Daten von Yahoo Finance
    yf_ticker = yf.Ticker(ticker)
    try:
        data = yf_ticker.history(interval=timeframe, start=start_str, end=end_str)
        data.reset_index(inplace=True)
        #print("Daten erfolgreich abgerufen!")  
    except Exception as e:
        print(f"Fehler beim Abrufen der Daten für {ticker}: {e}")
        return None

    if data.empty:
        print(f"Keine Daten für {ticker} im Zeitraum {start_str} bis {end_str}")
        return None

    #print(f"Erfolgreich Daten abgerufen: {data.head()}")  # Ausgabe der ersten paar Zeilen der Daten
    return transform_data(data, ticker)
    #return data

"""

def transform_data(data, symbol_id):

    transformed_data = pd.DataFrame()
    try:
        data['date'] = pd.to_datetime(data['Datetime'])
        data['symbol_id'] = symbol_id
        data = data.set_index(['date', 'symbol_id'])
        for index, row in data.iterrows():
            transformed_data.append({
                'symbol_id': index[1],
                'date': index[0],
                'open': row['Open'],
                'high': row['High'],
                'low': row['Low'],
                'close': row['Close'],
                'volume': row['Volume']
            })
    except KeyError as e:
        print(f"Fehler beim Transformieren der Daten: Spalte {e} nicht gefunden.")
        return None
    except Exception as e:
        print(f"Allgemeiner Fehler beim Transformieren der Daten: {e}")
        return None
    return transformed_data

"""

def transform_data(data, symbol_id):
    """
    Transformiert die abgerufenen Daten in das Format, das für die Datenbank benötigt wird.
    
    Parameters:
    data: DataFrame mit den abgerufenen Marktdaten.
    symbol_id: Die ID des Symbols in der Datenbank.
    
    Returns:
    Ein DataFrame, das die transformierten Daten darstellt.
    """
    transformed_data = pd.DataFrame()
    try:
        data['date'] = pd.to_datetime(data['Datetime'])
        data['symbol_id'] = symbol_id
        data = data.set_index(['date', 'symbol_id'])
        
        transformed_data = data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        transformed_data.columns = ['open', 'high', 'low', 'close', 'volume']
        transformed_data.reset_index(inplace=True)
        
    except KeyError as e:
        print(f"Fehler beim Transformieren der Daten: Spalte {e} nicht gefunden.")
        return None
    except Exception as e:
        print(f"Allgemeiner Fehler beim Transformieren der Daten: {e}")
        return None
    return transformed_data

if __name__ == "__main__":
    # Beispiel
    row = {
        'ticker': 'AAPL',
        #'ticker': 'EURUSD=X',
        'name': 'Euro-Dollar',
        'market': 'forex',
        'exchange': 'Yahoo Finance',
        'start_date': '2024-09-01',
        'last_update': '2024-10-01',  
        'timeframe': '5m',
        'active': 1
    }

    # Daten abrufen
    
    bars = load_yf_data(row)

    if bars is not None:
        # Speichern der Daten in eine CSV-Datei
        bars.to_csv(f"{row['ticker']}_data.csv", index=False)
        #print(f"Daten wurden in {row['ticker']}_data.csv gespeichert.")
        print(bars)
    else:
        print("Keine Daten zum Anzeigen.")