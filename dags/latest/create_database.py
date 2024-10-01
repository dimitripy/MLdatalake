import os
import json
import pandas as pd
import numpy as np
import yaml
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import enum
import subprocess
import sys

# Überprüfen und installieren Sie pymysql, falls es nicht vorhanden ist
def ensure_pymysql_installed():
    try:
        import pymysql
        print("pymysql ist bereits installiert.")
    except ImportError:
        print("pymysql ist nicht installiert. Installation wird durchgeführt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pymysql"])
        print("pymysql wurde erfolgreich installiert.")

# Lade die Konfigurationsdatei
def load_config(config_file_path):
    with open(config_file_path, 'r') as file:
        config = json.load(file)
    return config

# Verbindungsschema für MySQL
def create_db_engine(config):
    ensure_pymysql_installed()  # Sicherstellen, dass pymysql installiert ist
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

# Tabellendefinitionen
class Symbol(Base):
    __tablename__ = 'symbol'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    market = Column(Enum(Market), nullable=False)
    active = Column(Boolean, nullable=False)

class MinuteBar(Base):
    __tablename__ = 'minute_bar'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    symbol_id = Column(Integer, ForeignKey('symbol.id', ondelete="CASCADE"), nullable=False)
    symbol = relationship('Symbol', backref='minute_bars')

class FiveMinuteBar(Base):
    __tablename__ = 'five_minute_bar'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    symbol_id = Column(Integer, ForeignKey('symbol.id', ondelete="CASCADE"), nullable=False)
    symbol = relationship('Symbol', backref='five_minute_bars')

class ThirtyMinuteBar(Base):
    __tablename__ = 'thirty_minute_bar'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    symbol_id = Column(Integer, ForeignKey('symbol.id', ondelete="CASCADE"), nullable=False)
    symbol = relationship('Symbol', backref='thirty_minute_bars')

def main():
    try:
        # Pfad zur config.json Datei
        config_path = '/opt/airflow/dags/mldatalake/latest/config.json'
        
        # Einlesen der Konfigurationsdatei
        config = load_config(config_path)
        
        # Erstellen der Datenbank-Engine
        engine = create_db_engine(config)
        Base.metadata.create_all(engine)
        print("Tables created successfully")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

# Exportieren der Klassen
__all__ = ['Symbol', 'Market', 'MinuteBar']