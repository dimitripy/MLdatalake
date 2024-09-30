#!/bin/bash

# Aktuelles Verzeichnis des Skripts herausfinden
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ableiten des Quellverzeichnisses (angenommen, es ist relativ zum Skriptverzeichnis)
SOURCE_DIR="$(realpath "${SCRIPT_DIR}/../datalake_dags")"

# Prüfen, ob das Quellverzeichnis existiert
if [ ! -d "$SOURCE_DIR" ];then
  echo "Quellverzeichnis $SOURCE_DIR existiert nicht."
  exit 1
fi

# Registrierung und Sync-Triggerskript finden
REGISTRY_SCRIPT="$(realpath "${SCRIPT_DIR}/registry.sh")"

if [ ! -f "$REGISTRY_SCRIPT" ];then
  echo "registry.sh Skript nicht gefunden. Stelle sicher, dass es im selben Verzeichnis liegt wie dieses Skript."
  exit 1
fi

# Projektname und DAG-Pfad bestimmen
PROJECT_NAME=$(basename "$SOURCE_DIR")
DAG_PATH="$SOURCE_DIR"  # Der absolute Pfad wurde bereits mit `realpath` ermittelt

# Backup-Verzeichnis und Pfad zur API-Schlüsseldatei bestimmen
BACKUP_DIR="$(realpath "${SCRIPT_DIR}/../backups")"
API_KEY_FILE="$(realpath "${SCRIPT_DIR}/../config/key.txt")"

# Überprüfen, ob die Pfade korrekt gesetzt sind
echo "DAG_PATH: $DAG_PATH"
echo "BACKUP_DIR: $BACKUP_DIR"
echo "API_KEY_FILE: $API_KEY_FILE"

# Unterprojekt in der Registry registrieren und Sync-DAG triggern
bash "$REGISTRY_SCRIPT" "$PROJECT_NAME" "$DAG_PATH" "$BACKUP_DIR" "$API_KEY_FILE"