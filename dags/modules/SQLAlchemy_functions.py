import os
import json
import enum
import pandas as pd
import subprocess
import sys
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
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    symbol_id = Column(Integer, ForeignKey('symbol.id', ondelete="CASCADE"), nullable=False)
    symbol = relationship('Symbol')

class MinuteBar(TimeBarMixin, Base):
    __tablename__ = 'minute_bar'

class FiveMinuteBar(TimeBarMixin, Base):
    __tablename__ = 'five_minute_bar'

class ThirtyMinuteBar(TimeBarMixin, Base):
    __tablename__ = 'thirty_minute_bar'

# Sitzung starten und Tabellen erstellen
def start_session(config_path):
    if config_path is None:
        try:
            config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'customs/modules/config.json'))
            config = load_config(config_path)
        except Exception as e:
            print(f"Fehler beim Laden der Konfigurationsdatei: {e}, 'customs/modules/config.json' existiert nicht.")
            return None
    config = load_config(config_path)
    engine = create_db_engine(config)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    print("Session und Tabellen erfolgreich erstellt.")
    return Session()

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
