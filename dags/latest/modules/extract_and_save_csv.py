# extract_and_save_csv.py

import pandas as pd
from zipfile import ZipFile

def extract_and_save_csv(zip_file_path, output_csv_path):
    with ZipFile(zip_file_path) as zf:
        cols = ['time', 'open', 'high', 'low', 'close', 'volume']
        dfs = pd.concat({text_file.filename.split('.')[0]: pd.read_csv(zf.open(text_file.filename), usecols=cols)
                         for text_file in zf.infolist() if text_file.filename.endswith('.csv')})
    
    df = dfs.droplevel(1).reset_index().rename(columns={'index': 'ticker'})
    df = df[df['ticker'].str.contains('usd')]
    df['date'] = pd.to_datetime(df['time'], unit='ms')
    df = df.sort_values(by=['date', 'ticker']).drop(columns='time').set_index(['date', 'ticker'])
    
    df.to_csv(output_csv_path)
    print(f"CSV-Datei wurde erfolgreich unter {output_csv_path} gespeichert.")

if __name__ == "__main__":
    zip_file_path = './archive.zip'
    output_csv_path = './gespeicherter_dataframe.csv'
    extract_and_save_csv(zip_file_path, output_csv_path)