import os
import mysql.connector
from dotenv import load_dotenv

# Lade die Umgebungsvariablen aus der .env Datei
load_dotenv()  # Diese Funktion lädt die Variablen aus der .env-Datei

# Hole die Umgebungsvariablen
mysql_host = os.getenv('MYSQL_HOST', 'localhost')  # Standardmäßig 'localhost', falls nicht gesetzt
mysql_user = os.getenv('MYSQL_USER', 'root')
mysql_password = os.getenv('MYSQL_PASSWORD', 'root')
mysql_database = os.getenv('MYSQL_DATABASE', 'mydatabase')
mysql_port = int(os.getenv('MYSQL_PORT', 3306))

# Ausgabe der geladenen Umgebungsvariablen
print("Geladene Umgebungsvariablen:")
print(f"MYSQL_HOST: {mysql_host}")
print(f"MYSQL_USER: {mysql_user}")
print(f"MYSQL_PASSWORD: {'*****' if mysql_password else 'Nicht gesetzt'}")  # Vermeide das direkte Ausgeben des Passworts
print(f"MYSQL_DATABASE: {mysql_database}")
print(f"MYSQL_PORT: {mysql_port}")

# Prüfe, ob alle erforderlichen Umgebungsvariablen geladen sind
required_vars = [mysql_user, mysql_password, mysql_database]
if any(var is None for var in required_vars):
    print("Fehler: Eine oder mehrere erforderliche Umgebungsvariablen fehlen.")
    exit(1)

# Stelle sicher, dass die Umgebungsvariablen geladen sind und verbinde zur Datenbank
try:
    connection = mysql.connector.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database,
        port=mysql_port
    )
    print("Verbindung zur Datenbank erfolgreich")

    # Beispielabfrage
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    print("Tabellen:", tables)

except mysql.connector.Error as err:
    print(f"Fehler bei der Verbindung zur Datenbank: {err}")
finally:
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("Verbindung zur Datenbank geschlossen.")