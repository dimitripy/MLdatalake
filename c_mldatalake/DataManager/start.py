from Uploader import DatabaseUploader
import logging

def main():
    uploader = DatabaseUploader("/home/ageq/Git_Projects/MLdatalake/c_mldatalake/DataManager/config.json")

    uploader.add_symbol(ticker="AAPL-USD", name="Apple Inc.", market="stock", exchange="Yahoo Finance", sector="Technology", category="EQUITY")

    df = uploader.set_csv_path("/home/ageq/Git_Projects/MLdatalake/AAPL_data.csv") #, additional_data={'extra_column': 'value'}

    # Verwende den Schema-Namen als String

    validation_status = uploader.validate_data(df, "Yahoo Finance")

    if validation_status['status'] == "success":
        uploader._start_session()
        upload_status = uploader.upload_data("minute_bar", df)
        uploader.close_session()
        print(upload_status)
    else:
        print(validation_status)

if __name__ == "__main__":


# Logging konfigurieren
    logging.basicConfig(
        level=logging.INFO,  # Setze das gewünschte Logging-Level (z.B. DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Beispiel: Änderung des Logging-Levels zu DEBUG, um detailliertere Logs zu sehen
    logging.getLogger().setLevel(logging.DEBUG)
    main()