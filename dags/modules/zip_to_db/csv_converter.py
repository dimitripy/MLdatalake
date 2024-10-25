# csv_converter.py
import os
import pandas as pd

def convert_csv_files(extract_to_path, output_csv_path):
    """Wandelt alle CSV-Dateien in einem Verzeichnis in eine kombinierte CSV-Datei um."""
    cols = ['time', 'open', 'high', 'low', 'close', 'volume']
    first_file = True
    file_count = 0
    
    # Zählen der CSV-Dateien im Verzeichnis
    total_files = sum(
        len(files) for r, d, files in os.walk(extract_to_path) if any(f.endswith('.csv') for f in files)
    )
    
    for root, dirs, files in os.walk(extract_to_path):
        for file in files:
            if file.endswith('.csv'):
                file_count += 1
                print(f"Verarbeite Datei {file_count} von {total_files}: {file}")
                #TODO - Dateigröße und zeitliche Dauer der Verarbeitung berechnen + Animation
                file_path = os.path.join(root, file)
                df = pd.read_csv(file_path, usecols=cols)
                df['ticker'] = file.split('.')[0]
                df = df[df['ticker'].str.contains('usd')]
                df['date'] = pd.to_datetime(df['time'], unit='ms')
                df = df.sort_values(by=['date', 'ticker']).drop(columns='time').set_index(['date', 'ticker'])
                
                # Erstellen oder Anhängen der Daten zur Ausgabedatei
                if first_file:
                    df.to_csv(output_csv_path, mode='w', header=True)
                    first_file = False
                else:
                    df.to_csv(output_csv_path, mode='a', header=False)
    
    print(f"CSV-Datei wurde erfolgreich unter {output_csv_path} gespeichert.")

def main_convert_csv(extract_to_path='/home/ageq/Git_Projects/MLdatalake/source/archive', 
                     output_csv_path='/home/ageq/Git_Projects/MLdatalake/source/combined.csv'):
    """Hauptfunktion für die CSV-Konvertierung."""
    try:
        convert_csv_files(extract_to_path, output_csv_path)
    except Exception as e:
        print(f"An error occurred: {e}")
