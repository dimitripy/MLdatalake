#!/bin/bash
# create_database.sh - Skript zur Erstellung und Initialisierung der MySQL-Datenbank

# Setze die Zeitsynchronisation, falls notwendig (optional)
sudo timedatectl set-ntp true
sudo timedatectl

# Aktuelles Verzeichnis des Skripts herausfinden
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die Umgebungsvariablen aus der .env Datei
ENV_FILE="$SCRIPT_DIR/../.env"
echo "Pfad zur .env Datei: $ENV_FILE"

if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo "Fehler: Die .env Datei wurde nicht gefunden."
    exit 1
fi

# Navigiere zum Verzeichnis mit der docker-compose.yml
COMPOSE_DIR="$SCRIPT_DIR/../mldatalake/"
cd "$COMPOSE_DIR"

# Starte die Container mit Docker Compose
echo "Starte die Container mit Docker Compose..."
docker-compose up -d

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

echo "MySQL-Datenbank wurde erfolgreich gestartet und initialisiert."
