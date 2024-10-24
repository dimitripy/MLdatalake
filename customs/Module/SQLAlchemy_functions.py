#Stand: funktionstüchtig
# TODO eventuell noch erweiterbar um weitere Tabellen für andere Assets 

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import json
import os

# Sitzung und Basis erstellen
Base = declarative_base()

class Symbol(Base):
    __tablename__ = 'symbol'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    market = Column(Enum('crypto', 'stock', 'forex', 'futures'), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    
    def __repr__(self):
        return f"<Symbol(ticker={self.ticker}, name={self.name}, market={self.market})>"

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
    symbol = relationship('Symbol', backref='five_minute_bar')

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
    symbol = relationship('Symbol', backref='thirty_minute_bar')

def get_db_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

def load_config(config_file_path):
    with open(config_file_path, 'r') as file:
        config = json.load(file)
    return config

def create_db_engine(config):
    db_type = "mysql+pymysql"
    url = f"{db_type}://{config['db_user']}:{config['db_password']}@{config['db_host']}:{config['db_port']}/{config['db_name']}"
    return create_engine(url, echo=False)

def create_tables(engine):
    Base.metadata.create_all(engine)

def start_session():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'customs/Module/config.json'))
    config = load_config(config_path)
    engine = create_db_engine(config)
    session = get_db_session(engine)
    create_tables(engine)
    print("session started")
    return session

if __name__ == "__main__":

    session = start_session()