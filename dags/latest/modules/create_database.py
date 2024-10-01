#craete_database.py

import os
import json
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import enum

# Lade die Konfigurationsdatei
def load_config(config_file_path):
    with open(config_file_path, 'r') as file:
        config = json.load(file)
    return config

# Verbindungsschema für MySQL
def create_db_engine(config):
    db_type = "mysql+pymysql"
    url = f"{db_type}://{config['db_user']}:{config['db_password']}@{config['db_host']}/{config['db_name']}"
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

def main(config_file_path):
    config = load_config(config_file_path)
    engine = create_db_engine(config)
    Base.metadata.create_all(engine)
    print("Tables created successfully")

if __name__ == "__main__":
    import sys
    main(sys.argv[1])

# Exportieren der Klassen
__all__ = ['Symbol', 'Market', 'MinuteBar']