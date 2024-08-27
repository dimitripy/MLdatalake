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
