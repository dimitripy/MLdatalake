
import pandas as pd
from sqlalchemy import create_engine, text
import logging
from schemas import SCHEMAS
from enum import Enum

class TableName(Enum):
    MINUTE_BAR = "minute_bar"

class DatabaseUploader:
    def __init__(self, vault_client, secret_path):
        self.engine = None
        self.csv_path = None
        self.config = None
        self.vault_client = vault_client
        self.secret_path = secret_path
        self._start_session()
        self.close_session()

    def _get_db_credentials_from_vault(self):
        return self.vault_client.get_secret(self.secret_path)

    def _start_session(self):
        try:
            db_details = self._get_db_credentials_from_vault()
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

    def get_table_enum(table_name_str):
        try:
            return TableName[table_name_str.upper().replace(" ", "_")]
        except KeyError:
            raise ValueError(f"Ungültiger Tabellenname: {table_name_str}")

    def upload_data(self, df, table_name, source_name):
        try:
            table= TableName[table_name.upper().replace(" ", "_")]
        except KeyError:
            raise ValueError(f"Ungültiger Tabellenname: {table_name}")
        
        validation_status = self.validate_data(df, source_name)
        
        if validation_status['status'] != "success":
            return validation_status
        
        try:
            df = self.preprocess_data(df)
            data = df.to_dict(orient='records')

            with self.engine.connect() as connection:
                transaction = connection.begin()
                try:
                    # Verwende das Enum, um den Tabellennamen sicher zu beziehen
                    insert_query = f"""
                        INSERT INTO {table.value} (date, sy_id, open, high, low, close, volume)
                        VALUES (:date, :sy_id, :open, :high, :low, :close, :volume)
                        ON DUPLICATE KEY UPDATE
                        open = VALUES(open), high = VALUES(high), low = VALUES(low),
                        close = VALUES(close), volume = VALUES(volume)
                    """
                    connection.execute(text(insert_query), data)
                    transaction.commit()
                    logging.info("Daten erfolgreich hochgeladen, Duplikate behandelt.")
                    return {"status": "success", "message": "Daten erfolgreich hochgeladen."}
                except Exception as e:
                    transaction.rollback()
                    logging.error(f"Fehler beim Hochladen der Daten: {e}")
                    return {"status": "error", "message": str(e)}
        except Exception as e:
            logging.error(f"Fehler beim Verarbeiten der Daten: {e}")
            return {"status": "error", "message": str(e)}