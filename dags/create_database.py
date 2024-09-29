import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv
import enum

# Lade die Umgebungsvariablen aus der .env Datei
load_dotenv()  # Diese Funktion lädt die Variablen aus der .env-Datei

# Hole die Umgebungsvariablen
mysql_host = os.getenv('MYSQL_HOST', 'localhost')  # Standardmäßig 'localhost', falls nicht gesetzt
mysql_user = os.getenv('MYSQL_USER', 'root')
mysql_password = os.getenv('MYSQL_PASSWORD', 'root')
mysql_database = os.getenv('MYSQL_DATABASE', 'mydatabase')
mysql_port = int(os.getenv('MYSQL_PORT', 3306))

# Verbindungsschema für MySQL
db_type = "mysql+pymysql"
url = f"{db_type}://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
engine = create_engine(url, echo=False)

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

print("Tables created successfully")