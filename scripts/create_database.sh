#!/bin/bash
# create_database.sh - Skript zur Erstellung und Initialisierung der MySQL-Datenbank

# Setze die Zeitsynchronisation, falls notwendig (optional)
sudo timedatectl set-ntp true
sudo timedatectl

# Aktuelles Verzeichnis des Skripts herausfinden
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die Umgebungsvariablen aus der .env Datei
ENV_FILE="$SCRIPT_DIR/../.env"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo "Fehler: Die .env Datei wurde nicht gefunden."
    exit 1
fi

# Setze den Pfad, wo die Daten auf deinem Host-System gespeichert werden sollen
HOST_DB_PATH="$SCRIPT_DIR/../mldatalake/database_data"

# Sicherstellen, dass das Verzeichnis existiert
mkdir -p "$HOST_DB_PATH"

# Baue das Docker-Image für MySQL
echo "Baue das Docker-Image für MySQL..."
docker build -t datalake-db ./mysql

# Starte den MySQL-Container mit den Umgebungsvariablen aus der .env Datei
echo "Starte den MySQL-Container..."
docker run -d \
  --name datalake \
  -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD \
  -e MYSQL_DATABASE=$MYSQL_DATABASE \
  -e MYSQL_USER=$MYSQL_USER \
  -e MYSQL_PASSWORD=$MYSQL_PASSWORD \
  -v "$HOST_DB_PATH":/var/lib/mysql \
  -p $MYSQL_PORT:3306 \
  datalake-db

# Warte auf den MySQL-Container und prüfe bis zu 8 Versuche, ob er läuft
MAX_ATTEMPTS=8
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "Warte auf MySQL-Container... Versuch $ATTEMPT von $MAX_ATTEMPTS"
    sleep 5

    # Prüfe, ob der Container läuft
    if [ "$(docker inspect -f '{{.State.Running}}' datalake)" = "true" ]; then
        echo "MySQL-Container läuft erfolgreich."
        break
    fi

    ATTEMPT=$((ATTEMPT + 1))
done

# Falls der Container nach allen Versuchen nicht gestartet ist, Fehler melden
if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
    echo "Fehler: MySQL-Container konnte nach $MAX_ATTEMPTS Versuchen nicht gestartet werden."
    exit 1
fi

# Weitere Initialisierungen können hier hinzugefügt werden
echo "MySQL-Datenbank wurde erfolgreich gestartet und initialisiert."
