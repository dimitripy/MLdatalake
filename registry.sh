#!/bin/bash

# Pfad zur globalen Registry-Datei
REGISTRY_FILE="$HOME/.airflow_dag_registry.yaml"

register_in_registry() {
  PROJECT_NAME=$1
  DAG_PATH=$2

  echo "Registriere Unterprojekt in der globalen DAG-Registry..."

  # Überprüfen, ob die Registry-Datei existiert
  if [ ! -f "$REGISTRY_FILE" ]; then
    echo "Registry-Datei $REGISTRY_FILE existiert nicht. Erstelle sie..."
    echo "# Globale DAG Registry File" > "$REGISTRY_FILE"
    echo "# List of registered submodules and their DAG paths" >> "$REGISTRY_FILE"
  fi

  # Überprüfen, ob das Projekt bereits in der Registry eingetragen ist
  if grep -q "^  $PROJECT_NAME:" "$REGISTRY_FILE"; then
    echo "Das Unterprojekt $PROJECT_NAME ist bereits in der Registry registriert."
  else
    # Projekt zur Registry hinzufügen
    echo "  $PROJECT_NAME:" >> "$REGISTRY_FILE"
    echo "    dag_path: $DAG_PATH" >> "$REGISTRY_FILE"
    echo "Unterprojekt $PROJECT_NAME wurde erfolgreich in die Registry eingetragen."
  fi
}

trigger_sync_dag() {
  echo "Trigger den 'sync_dags' DAG in Airflow im Docker-Container..."

  # Name des Docker Compose Service (anpassen, falls anders)
  SERVICE_NAME="mlscope-airflow-scheduler-1"

  # Überprüfen, ob der Service läuft (Docker Compose sollte im Verzeichnis sein)
  if ! docker-compose ps | grep -q "$SERVICE_NAME"; then
    echo "Der Service '$SERVICE_NAME' läuft nicht. Bitte stelle sicher, dass der Airflow-Container läuft und versuche es erneut."
    exit 1
  fi

  # Trigger den DAG innerhalb des Containers
  docker-compose exec "$SERVICE_NAME" airflow dags trigger sync_dags

  if [ $? -eq 0 ]; then
    echo "Der DAG 'sync_dags' wurde erfolgreich im Docker-Container getriggert."
  else
    echo "Fehler beim Triggern des DAGs 'sync_dags' im Docker-Container."
  fi
}

# Überprüfen, ob die erforderlichen Argumente übergeben wurden
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <PROJECT_NAME> <DAG_PATH>"
  exit 1
fi

# Aufruf der Funktion zur Registrierung
register_in_registry "$1" "$2"

# Trigger den Sync-DAG nach der Registrierung
trigger_sync_dag
