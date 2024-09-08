import os
import pandas as pd
import zipfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from create_database import Base, Symbol, Market

def load_env_variables():
    load_dotenv()
    return {
        'mysql_host': os.getenv('MYSQL_HOST', 'localhost'),
        'mysql_user': os.getenv('MYSQL_USER', 'root'),
        'mysql_password': os.getenv('MYSQL_PASSWORD', 'root'),
        'mysql_database': os.getenv('MYSQL_DATABASE', 'mydatabase'),
        'mysql_port': int(os.getenv('MYSQL_PORT', 3306))
    }

def create_db_engine(env_vars):
    db_type = "mysql+pymysql"
    url = f"{db_type}://{env_vars['mysql_user']}:{env_vars['mysql_password']}@{env_vars['mysql_host']}:{env_vars['mysql_port']}/{env_vars['mysql_database']}"
    return create_engine(url, echo=False)

def extract_zip(zip_file_path, extract_to='.'):
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def read_csv(file_path):
    return pd.read_csv(file_path)

def process_data(df):
    df['active'] = df['active'].astype(bool)
    df['market'] = df['market'].apply(lambda x: x.upper())
    return df

def import_data_to_db(session, df):
    for index, row in df.iterrows():
        symbol = Symbol(
            ticker=row['ticker'],
            name=row['name'],
            market=Market[row['market']],
            active=row['active']
        )
        session.add(symbol)
    session.commit()

def main():
    try:
        env_vars = load_env_variables()
        engine = create_db_engine(env_vars)
        Session = sessionmaker(bind=engine)
        session = Session()

        zip_file_path = 'data.zip'
        csv_file_name = 'data.csv'
        extract_to = './extracted_data'

        if not os.path.exists(os.path.join(extract_to, csv_file_name)):
            extract_zip(zip_file_path, extract_to)

        df = read_csv(os.path.join(extract_to, csv_file_name))
        df = process_data(df)
        import_data_to_db(session, df)

        print("Data imported successfully")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()