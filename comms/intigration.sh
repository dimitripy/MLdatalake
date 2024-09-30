#!/bin/bash
#intigration.sh

# Überprüfen, ob mindestens ein Argument übergeben wurde
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <PROJECT_NAME> [KEY=VALUE]..."
  exit 1
fi

PROJECT_NAME=$1
shift  # Entferne den ersten Parameter (Projektname)

# Aktuelles Verzeichnis des Skripts herausfinden
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Registrierung und Sync-Triggerskript finden
REGISTRY_SCRIPT="$(realpath "${SCRIPT_DIR}/registry.sh")"

if [ ! -f "$REGISTRY_SCRIPT" ]; then
  echo "registry.sh Skript nicht gefunden. Stelle sicher, dass es im selben Verzeichnis liegt wie dieses Skript."
  exit 1
fi

# Unterprojekt in der Registry registrieren und Sync-DAG triggern
bash "$REGISTRY_SCRIPT" "$PROJECT_NAME" "$@"