#!/bin/bash

# Aktuelles Verzeichnis des Skripts herausfinden
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ableiten des Quellverzeichnisses (angenommen, es ist relativ zum Skriptverzeichnis)
SOURCE_DIR="${SCRIPT_DIR}/../MLdatalake/datalake_dags"

# Prüfen, ob das Quellverzeichnis existiert
if [ ! -d "$SOURCE_DIR" ]; then
  echo "Quellverzeichnis $SOURCE_DIR existiert nicht."
  exit 1
fi

# Registrierung und Sync-Triggerskript finden
REGISTRY_SCRIPT="${SCRIPT_DIR}/registry.sh"

if [ ! -f "$REGISTRY_SCRIPT" ]; then
  echo "registry.sh Skript nicht gefunden. Stelle sicher, dass es im selben Verzeichnis liegt wie dieses Skript."
  exit 1
fi

# Projektname und DAG-Pfad bestimmen
PROJECT_NAME=$(basename "$SOURCE_DIR")
DAG_PATH="$(realpath "$SOURCE_DIR")"  # Nutze `realpath` für den absoluten Pfad

# Unterprojekt in der Registry registrieren und Sync-DAG triggern
bash "$REGISTRY_SCRIPT" "$PROJECT_NAME" "$DAG_PATH"
