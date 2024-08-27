#!/bin/bash

# Aktuelles Verzeichnis des Skripts herausfinden
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lese die Konfigurationen aus der JSON-Datei
DB_CONF_FILE="$SCRIPT_DIR/db_conf.json"
DB_HOST=$(jq -r '.host' "$DB_CONF_FILE")
DB_NAME=$(jq -r '.database' "$DB_CONF_FILE")
CONTAINER_NAME="crypto_app"
IMAGE_NAME="crypto_app_image"
SCRIPT_NAME="create_database.py"  # Der Name deines Python-Skripts

# Setze den Pfad, wo die Daten auf deinem Host-System gespeichert werden sollen
HOST_DB_PATH="$SCRIPT_DIR/../database_data"

# Sicherstellen, dass das Verzeichnis existiert
mkdir -p "$HOST_DB_PATH"

# Docker-Image bauen
echo "Baue Docker-Image..."
docker build -t $IMAGE_NAME "$SCRIPT_DIR"

# Docker-Container starten und das Datenverzeichnis mounten
echo "Starte Docker-Container mit Datenbank-Mount..."
docker run -d --name $CONTAINER_NAME \
  -v "$HOST_DB_PATH:/var/lib/mysql" \
  $IMAGE_NAME

# Warte kurz, bis der Container vollständig gestartet ist
sleep 5

# Führe das Python-Skript im Container aus, um die Datenbank zu initialisieren
echo "Initialisiere die Datenbank im Docker-Container..."
docker exec -it $CONTAINER_NAME python $SCRIPT_NAME

echo "Docker-Container $CONTAINER_NAME gestartet und die Datenbank wurde initialisiert."
