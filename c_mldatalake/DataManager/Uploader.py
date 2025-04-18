import json
import pandas as pd
from sqlalchemy import create_engine, text
import logging
from schemas import SCHEMAS

class DatabaseUploader:
    def __init__(self, config_path):
        self.engine = None
        self.csv_path = None
        self.config = None
        self._load_config(config_path)
        self._start_session()
        self.close_session()

    def _load_config(self, config_path):
        try:
            with open(config_path, 'r') as config_file:
                self.config = json.load(config_file)
            logging.info("Konfigurationsdaten erfolgreich geladen.")
        except Exception as e:
            logging.error(f"Fehler beim Laden der Konfigurationsdaten: {e}")
            raise

    def _start_session(self):
        try:
            db_details = self.config
            self.engine = create_engine(
                f"mysql+mysqlconnector://{db_details['db_user']}:{db_details['db_password']}@"
                f"{db_details['db_host']}:{db_details['db_port']}/{db_details['db_name']}"
            )
            logging.info("Datenbankverbindung erfolgreich hergestellt.")
        except Exception as e:
            logging.error(f"Fehler bei der Herstellung der Datenbankverbindung: {e}")
            raise

    def close_session(self):
        if self.engine:
            self.engine.dispose()
            logging.info("Datenbankverbindung geschlossen.")

    def set_csv_path(self, csv_path, additional_data=None):
        self.csv_path = csv_path
        logging.info(f"CSV-Pfad gesetzt: {csv_path}")
        return self.process_csv(additional_data)

    def process_csv(self, additional_data=None):
        try:
            df = pd.read_csv(self.csv_path)
            if additional_data:
                for key, value in additional_data.items():
                    df[key] = value
            logging.info("CSV-Daten erfolgreich verarbeitet.")
            return df
        except Exception as e:
            logging.error(f"Fehler beim Verarbeiten der CSV-Daten: {e}")
            raise

    def validate_data(self, df, source_name):
        try:
            schema = SCHEMAS.get(source_name)
            if not schema:
                logging.error(f"Schema für {source_name} nicht gefunden.")
                return {"status": "error", "message": f"Schema für {source_name} nicht gefunden."}

            missing_columns = [col for col in schema['required_columns'] if col not in df.columns]
            if missing_columns:
                logging.info(f"Fehlende Spalten in CSV-Datei für {schema['source']}: {missing_columns}")
                return {"status": "warning", "missing_columns": missing_columns}

            logging.info(f"Alle erforderlichen Daten vorhanden für {schema['source']}.")
            return {"status": "success"}
        except Exception as e:
            logging.error(f"Fehler bei der Validierung der Daten: {e}")
            return {"status": "error", "message": str(e)}
        
    def add_symbol(self, ticker, name, market, exchange, category, sector):
        try:
            with self.engine.connect() as connection:
                transaction = connection.begin()
                try:
                    # Überprüfe, ob die Kombination aus exchange, category und sector bereits existiert
                    sec_id_query = text(
                        "SELECT sec_id FROM security WHERE exchange = :exchange AND category = :category AND sector = :sector"
                    )
                    sec_id_result = connection.execute(sec_id_query, {
                        'exchange': exchange,
                        'category': category,
                        'sector': sector
                    }).fetchone()

                    if not sec_id_result:
                        # Füge security ein, falls nicht vorhanden
                        insert_query = text(
                            "INSERT INTO security (exchange, category, sector) VALUES (:exchange, :category, :sector)"
                        )
                        connection.execute(insert_query, {
                            'exchange': exchange,
                            'category': category,
                            'sector': sector
                        })
                        sec_id = connection.execute(text("SELECT LAST_INSERT_ID()")).fetchone()[0]
                    else:
                        sec_id = sec_id_result[0]

                    # Prüfe Eindeutigkeit von symbol
                    symbol_query = text(
                        "SELECT sy_id FROM symbol WHERE ticker = :ticker AND sec_id = :sec_id"
                    )
                    symbol_result = connection.execute(symbol_query, {
                        'ticker': ticker,
                        'sec_id': sec_id
                    }).fetchone()

                    if symbol_result is None:
                        insert_symbol_query = text(
                            "INSERT INTO symbol (ticker, name, market, active, sec_id) VALUES (:ticker, :name, :market, :active, :sec_id)"
                        )
                        connection.execute(insert_symbol_query, {
                            'ticker': ticker,
                            'name': name,
                            'market': market,
                            'active': True, #TODO prüfung auf aktivität
                            'sec_id': sec_id
                        })
                        transaction.commit()
                        logging.info(f"Symbol {ticker} erfolgreich hinzugefügt.")
                    else:
                        logging.info(f"Symbol {ticker} existiert bereits.")
                except Exception as e:
                    transaction.rollback()
                    logging.error(f"Fehler beim Hinzufügen des Symbols: {e}")
                    raise
        except Exception as e:
            logging.error(f"Fehler beim Hinzufügen des Symbols: {e}")
            raise


    def resolve_sy_id(self, ticker):
        query = "SELECT sy_id FROM symbol WHERE ticker = :ticker"
        with self.engine.connect() as connection:
            result = connection.execute(text(query), {'ticker': ticker}).fetchone()
            if result:
                return result[0]  # Zugriff auf den ersten Eintrag im Tuple
            else:
                raise ValueError(f"Ticker {ticker} nicht in der `symbol`-Tabelle gefunden.")

    def preprocess_data(self, df):
        column_mapping = {'mdate': 'date', 'symbol_id': 'sy_id'}
        df = df.rename(columns=column_mapping)
        try:
            # Erstelle die 'sy_id'-Spalte
            df['sy_id'] = df['sy_id'].apply(lambda ticker: self.resolve_sy_id(ticker))
            # Entferne die 'ticker'-Spalte, wenn sie nicht benötigt wird
            #df = df.drop(columns=['ticker'])
        except Exception as e:
            logging.error(f"Fehler beim Zuweisen von `sy_id`: {e}")
            raise
        

        return df

    def upload_data(self, table_name, df):
        try:
            df = self.preprocess_data(df)
            with self.engine.connect() as connection:
                transaction = connection.begin()
                try:
                    df.to_sql(table_name, con=connection, if_exists='append', index=False)
                    transaction.commit()
                    logging.info("Daten erfolgreich hochgeladen.")
                    return {"status": "success"}
                except Exception as e:
                    transaction.rollback()
                    logging.error(f"Fehler beim Hochladen der Daten: {e}")
                    return {"status": "error", "message": str(e)}
        except Exception as e:
            logging.error(f"Fehler beim Verarbeiten der Daten: {e}")
            return {"status": "error", "message": str(e)}