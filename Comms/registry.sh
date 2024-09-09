#!/bin/bash

# Verzeichnis und Pfad zur zentralen Registry-Datei
REGISTRY_DIR="/etc/airflow"
REGISTRY_FILE="$REGISTRY_DIR/airflow_dag_registry.yaml"

register_in_registry() {
  PROJECT_NAME=$1
  DAG_PATH=$2
  BACKUP_DIR=$3
  API_KEY_FILE=$4

  echo "Registriere Unterprojekt in der zentralen DAG-Registry..."

  # Überprüfen, ob das Registry-Verzeichnis existiert
  if [ ! -d "$REGISTRY_DIR" ]; then
    echo "Registry-Verzeichnis $REGISTRY_DIR existiert nicht. Erstelle es..."
    sudo mkdir -p "$REGISTRY_DIR"
    sudo chmod 777 "$REGISTRY_DIR"  # Alle Benutzer dürfen in das Verzeichnis schreiben
  fi

  # Überprüfen, ob die Registry-Datei existiert
  if [ ! -f "$REGISTRY_FILE" ]; then
    echo "Registry-Datei $REGISTRY_FILE existiert nicht. Erstelle sie..."
    sudo touch "$REGISTRY_FILE"
    sudo chmod 666 "$REGISTRY_FILE"  # Alle Benutzer dürfen in die Datei schreiben
    echo "# Globale DAG Registry File" | sudo tee -a "$REGISTRY_FILE" > /dev/null
    echo "# List of registered submodules and their DAG paths" | sudo tee -a "$REGISTRY_FILE" > /dev/null
  fi

  # Überprüfen, ob das Projekt bereits in der Registry eingetragen ist
  if grep -q "^  $PROJECT_NAME:" "$REGISTRY_FILE"; then
    # Aktuellen Pfad des Projekts finden
    CURRENT_PATH=$(grep -A 3 "^  $PROJECT_NAME:" "$REGISTRY_FILE" | grep "dag_path:" | awk '{print $2}')
    
    # Überprüfen, ob der Pfad übereinstimmt
    if [ "$CURRENT_PATH" != "$DAG_PATH" ]; then
      echo "Der Pfad des Unterprojekts $PROJECT_NAME hat sich geändert. Aktualisiere den Eintrag..."
      
      # Aktualisieren des Pfads in der Registry
      sudo sed -i "/^  $PROJECT_NAME:/!b;n;c\    dag_path: $DAG_PATH" "$REGISTRY_FILE"
      sudo sed -i "/^  $PROJECT_NAME:/!b;n;n;c\    backup_dir: $BACKUP_DIR" "$REGISTRY_FILE"
      sudo sed -i "/^  $PROJECT_NAME:/!b;n;n;n;c\    api_key_file: $API_KEY_FILE" "$REGISTRY_FILE"
      echo "Der Pfad für das Unterprojekt $PROJECT_NAME wurde erfolgreich aktualisiert."
    else
      echo "Das Unterprojekt $PROJECT_NAME ist bereits mit dem richtigen Pfad in der Registry registriert."
    fi
  else
    # Projekt zur Registry hinzufügen
    echo "  $PROJECT_NAME:" | sudo tee -a "$REGISTRY_FILE" > /dev/null
    echo "    dag_path: $DAG_PATH" | sudo tee -a "$REGISTRY_FILE" > /dev/null
    echo "    backup_dir: $BACKUP_DIR" | sudo tee -a "$REGISTRY_FILE" > /dev/null
    echo "    api_key_file: $API_KEY_FILE" | sudo tee -a "$REGISTRY_FILE" > /dev/null
    echo "Unterprojekt $PROJECT_NAME wurde erfolgreich in die Registry eingetragen."
  fi
}

trigger_sync_dag() {
  echo "Trigger den 'sync_all_dags' DAG in Airflow im Docker-Container..."

  # Name des Docker Compose Service (anpassen, falls anders)
  SERVICE_NAME="mlcsope-airflow-scheduler-1"

  # Überprüfen, ob der Service läuft (Docker Compose sollte im Verzeichnis sein)
  if ! docker ps | grep -q "$SERVICE_NAME"; then
    echo "Der Service '$SERVICE_NAME' läuft nicht. Bitte stelle sicher, dass der Airflow-Container läuft und versuche es erneut."
    exit 1
  fi

  # Trigger den DAG innerhalb des Containers
  docker exec -it "$SERVICE_NAME" airflow dags trigger sync_all_dags

  if [ $? -eq 0 ]; then
    echo "Der DAG 'sync_all_dags' wurde erfolgreich im Docker-Container getriggert."
  else
    echo "Fehler beim Triggern des DAGs 'sync_all_dags' im Docker-Container."
  fi
}

show_registry_path() {
  echo "Der Pfad zur Registry-Datei ist: $REGISTRY_FILE"
}

# Überprüfen, ob die erforderlichen Argumente übergeben wurden
if [ "$#" -ne 4 ]; then
  echo "Usage: $0 <PROJECT_NAME> <DAG_PATH> <BACKUP_DIR> <API_KEY_FILE>"
  exit 1
fi

# Aufruf der Funktion zur Registrierung
register_in_registry "$1" "$2" "$3" "$4"

# Trigger den Sync-DAG nach der Registrierung
trigger_sync_dag

# Zeige den Pfad zur Registry-Datei
show_registry_path