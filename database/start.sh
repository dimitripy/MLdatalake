#!/bin/bash

# Lese die Konfigurationen aus der JSON-Datei
DB_HOST=$(jq -r '.host' db_conf.json)
DB_NAME=$(jq -r '.database' db_conf.json)
CONTAINER_NAME="crypto_app"
IMAGE_NAME="crypto_app_image"
SCRIPT_NAME="your_script.py"  # Der Name deines Python-Skripts

# Docker-Image bauen
echo "Baue Docker-Image..."
docker build -t $IMAGE_NAME .

# Docker-Container starten
echo "Starte Docker-Container..."
docker run -d --name $CONTAINER_NAME $IMAGE_NAME

# Warte kurz, bis der Container vollständig gestartet ist
sleep 5

# Führe das Python-Skript im Container aus, um die Datenbank zu initialisieren
echo "Initialisiere die Datenbank im Docker-Container..."
docker exec -it $CONTAINER_NAME python $SCRIPT_NAME

echo "Docker-Container $CONTAINER_NAME gestartet und die Datenbank wurde initialisiert."
