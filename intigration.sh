#!/bin/bash

# Aktuelles Verzeichnis des Skripts herausfinden
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ableiten des Quellverzeichnisses (angenommen, es ist relativ zum Skriptverzeichnis)
SOURCE_DIR="${SCRIPT_DIR}/../MLdatalake/airflow_dags"

# Ableiten des Zielverzeichnisses (angenommen, es ist ebenfalls relativ zum Skriptverzeichnis)
TARGET_DIR="${SCRIPT_DIR}/../MLscope/mlscope/airflow/dags"

# Prüfen, ob das Quellverzeichnis existiert
if [ ! -d "$SOURCE_DIR" ]; then
  echo "Quellverzeichnis $SOURCE_DIR existiert nicht."
  exit 1
fi

# Prüfen, ob das Zielverzeichnis existiert, ansonsten erstellen
if [ ! -d "$TARGET_DIR" ]; then
  echo "Zielverzeichnis $TARGET_DIR existiert nicht. Erstelle es..."
  mkdir -p "$TARGET_DIR"
fi

# Kopiere die Dateien vom Quell- ins Zielverzeichnis
cp -r "$SOURCE_DIR"/* "$TARGET_DIR"/

# Ausgabe zur Bestätigung
echo "DAGs wurden erfolgreich von $SOURCE_DIR nach $TARGET_DIR kopiert."

# Aufruf des Registrierungsskripts
PROJECT_NAME=$(basename "$SOURCE_DIR")
DAG_PATH="$TARGET_DIR"

# Annahme: `registry.sh` befindet sich im selben Verzeichnis wie dieses Skript
REGISTRY_SCRIPT="${SCRIPT_DIR}/registry.sh"

if [ ! -f "$REGISTRY_SCRIPT" ]; then
  echo "registry.sh Skript nicht gefunden. Stelle sicher, dass es im selben Verzeichnis liegt wie dieses Skript."
  exit 1
fi

# Unterprojekt in der Registry registrieren und Sync-DAG triggern
bash "$REGISTRY_SCRIPT" "$PROJECT_NAME" "$DAG_PATH"
