from Uploader import DatabaseUploader
import pandas as pd
import logging

def main():
    uploader = DatabaseUploader("/home/ageq/Git_Projects/MLdatalake/c_mldatalake/DataManager/config.json")

    # Symbol hinzufügen falls es neu sein sollte 
    uploader.add_symbol(ticker="AAPL-USD", name="Apple Inc.", market="stock", exchange="Yahoo Finance", sector="Technology", category="EQUITY")

    # CSV-Datei in einen DataFrame laden
    df = pd.read_csv("/home/ageq/Git_Projects/MLdatalake/AAPL_data.csv")

    # Daten validieren
    upload_status = uploader.upload_data( df, table_name="minute_bar", source_name="Yahoo Finance")
    print(upload_status)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logging.getLogger().setLevel(logging.DEBUG)
    main()