import json
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import enum

# Konfigurationen aus der JSON-Datei laden
with open('db_conf.json') as config_file:
    config = json.load(config_file)

# MySQL-Datenbankverbindung herstellen
db_type = config['db_type']
username = config['username']
password = config['password']
host = config['host']
port = config['port']
database = config['database']
echo = config['echo']

# Verbindungsschema für MySQL
url = f"{db_type}://{username}:{password}@{host}:{port}/{database}"
engine = create_engine(url, echo=echo)

# Sitzung und Basis erstellen
Session = sessionmaker(bind=engine)
session = Session()
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

# Tabellen erstellen
Base.metadata.create_all(engine)
