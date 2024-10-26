import os
import json
import enum
import pandas as pd
import subprocess
import sys
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship



# Überprüfen und installieren Sie erforderliche Bibliotheken
def install_dependencies():
    for package in ["pymysql", "cryptography"]:
        try:
            __import__(package)
            print(f"{package} ist bereits installiert.")
        except ImportError:
            print(f"{package} wird installiert...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{package} wurde erfolgreich installiert.")

# Lade Konfigurationsdatei
def load_config(config_file_path):
    with open(config_file_path, 'r') as file:
        return json.load(file)

# Erstelle Datenbank-Engine
def create_db_engine(config):
    install_dependencies()
    db_type = "mysql+pymysql"
    url = f"{db_type}://{config['db_user']}:{config['db_password']}@{config['db_host']}:{config['db_port']}/{config['db_name']}"
    return create_engine(url, echo=False)

# Sitzung und Basis erstellen
Base = declarative_base()

# Enum für den Markt
class Market(enum.Enum):
    crypto = 'crypto'
    stock = 'stock'
    forex = 'forex'
    futures = 'futures'

# Tabellenklassen
class Symbol(Base):
    __tablename__ = 'symbol'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    market = Column(Enum(Market), nullable=False)
    active = Column(Boolean, nullable=False)

class TimeBarMixin:
    @declared_attr
    def id(cls):
        return Column(Integer, primary_key=True, autoincrement=True)

    @declared_attr
    def date(cls):
        return Column(DateTime, nullable=False)

    @declared_attr
    def open(cls):
        return Column(Float)

    @declared_attr
    def high(cls):
        return Column(Float)

    @declared_attr
    def low(cls):
        return Column(Float)

    @declared_attr
    def close(cls):
        return Column(Float)

    @declared_attr
    def volume(cls):
        return Column(Float)

    @declared_attr
    def symbol_id(cls):
        return Column(Integer, ForeignKey('symbol.id', ondelete="CASCADE"), nullable=False)

    @declared_attr
    def symbol(cls):
        return relationship('Symbol')

class MinuteBar(TimeBarMixin, Base):
    __tablename__ = 'minute_bar'

class FiveMinuteBar(TimeBarMixin, Base):
    __tablename__ = 'five_minute_bar'

class ThirtyMinuteBar(TimeBarMixin, Base):
    __tablename__ = 'thirty_minute_bar'


def start_session(config_path=None, use_test_db=False):
    # Setze den Pfad zur Testkonfiguration, wenn `use_test_db` auf True gesetzt ist
    if use_test_db:
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_config.json'))
    elif config_path is None:
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.json'))
    
    try:
        config = load_config(config_path)
    except Exception as e:
        print(f"Fehler beim Laden der Konfigurationsdatei: {e}")
        return None
    
    try:
        engine = create_db_engine(config)
        Base.metadata.create_all(engine)  # Erstelle alle Tabellen
        Session = sessionmaker(bind=engine)
        print(f"Session und Tabellen für {'Test-' if use_test_db else ''}Datenbank erfolgreich erstellt.")
        return Session()
    except Exception as e:
        print(f"Fehler beim Erstellen der Datenbank-Engine: {e}")
        return None


# Allgemeine Funktion zum Einfügen von Daten
def insert_data(session, data, table_class, symbol_id):
    for _, row in data.iterrows():
        entry = table_class(
            date=row['date'],
            open=row['open'],
            high=row['high'],
            low=row['low'],
            close=row['close'],
            volume=row['volume'],
            symbol_id=symbol_id
        )
        session.add(entry)
    session.commit()

if __name__ == "__main__":
    config_path = '/opt/airflow/dags/mldatalake/latest/config.json'
    session = start_session(config_path)
