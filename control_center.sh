#!/bin/bash
# control_center.sh - Skript zur Verwaltung von MLdatalake

# Überprüfen, ob das Skript als Root-Benutzer ausgeführt wird
if [ "$EUID" -ne 0 ]; then
  echo "Bitte führen Sie dieses Skript als Root-Benutzer aus."
  exit 1
fi

# Gemeinsame Funktionen einbinden
source "$(dirname "${BASH_SOURCE[0]}")/comms/common_functions.sh"

# Verzeichnisse und Dateien definieren
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_DIR="$SCRIPT_DIR/"  # Verzeichnis mit der docker-compose.yml
ENV_FILE="$SCRIPT_DIR/.env"  # Pfad zur .env Datei
CONFIG_FILE="$SCRIPT_DIR/dags/latest/config.json"  # Pfad zur config.json Datei
CONFIG_DIR="$(dirname "$CONFIG_FILE")"  # Verzeichnis der config.json Datei
CREATE_DB_SCRIPT="$SCRIPT_DIR/customs/create_database.sh"  # Pfad zum create_database.sh Skript
INTEGRATION_SCRIPT="$SCRIPT_DIR/comms/intigration.sh"  # Pfad zum intigration.sh Skript
DAGS_DIR="$SCRIPT_DIR/dags"  # Pfad zu den DAGs
SOURCE_DIR="$SCRIPT_DIR/source"  # Pfad zum source Verzeichnis

# Definiere den Projektnamen für das Logging
PROJECT_NAME="mldatalake"

# Lade die Umgebungsvariablen aus der .env Datei
echo "Pfad zur .env Datei: $ENV_FILE"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo "Fehler: Die .env Datei wurde nicht gefunden."
    exit 1
fi

# Funktion zum Erstellen der config.json Datei
create_config_json() {
    # Stelle sicher, dass das Verzeichnis existiert
    mkdir -p "$CONFIG_DIR"
    
    cat <<EOF > "$CONFIG_FILE"
{
    "db_user": "$MYSQL_USER",
    "db_password": "$MYSQL_PASSWORD",
    "db_host": "datalake",
    "db_port": 3306,
    "db_name": "$MYSQL_DATABASE",
    "zip_file_name": "trimmed_file"
}
EOF
    echo "config.json Datei wurde erfolgreich erstellt unter $CONFIG_FILE"
}

# Funktion zum Löschen der config.json Datei
delete_config_json() {
    if [ -f "$CONFIG_FILE" ]; then
        rm "$CONFIG_FILE"
        echo "Alte config.json Datei wurde gelöscht."
    fi
}

# Funktion zum Löschen aller benutzerdefinierten Datenbanken
delete_all_databases() {
    docker exec -i datalake mysql -u root -p"$MYSQL_ROOT_PASSWORD" <<EOF
    SET FOREIGN_KEY_CHECKS = 0;
    $(docker exec -i datalake mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "SHOW DATABASES;" | grep -Ev "(Database|information_schema|mysql|performance_schema|sys)" | awk '{print "DROP DATABASE " $1 ";"}')
    SET FOREIGN_KEY_CHECKS = 1;
EOF
    echo "Alle benutzerdefinierten Datenbanken wurden gelöscht."
}

# Initialisierungsfunktion
initialize_project() {
    log "$PROJECT_NAME" "Starte Initialisierung des Projekts..."

    # Registriere in der zentralen Registry und trigger den Sync-DAG
    if [ -f "$INTEGRATION_SCRIPT" ]; then
        bash "$INTEGRATION_SCRIPT" "$PROJECT_NAME" \
            "dag_path=$DAGS_DIR" \
            "source_path=$SOURCE_DIR"

    else
        echo "intigration.sh Skript nicht gefunden unter $INTEGRATION_SCRIPT"
        exit 1
    fi

    log "$PROJECT_NAME" "Initialisierung des Projekts abgeschlossen."
}

# Funktion zum Verbinden der Airflow-Container mit dem mldatalake_default-Netzwerk
connect_network() {
    docker network connect mlscope_default datalake
    echo "MySQL-Container wurde mit dem mlscope_default-Netzwerk verbunden."
}

# Menü für Benutzerinteraktion
echo "Bitte wähle eine Option:"
echo "1 - Datenbank erstellen und initialisieren"
echo "2 - config.json Datei erstellen"
echo "3 - Starten oder Neustarten des Docker-Containers"
echo "5 - Stoppen des Docker-Containers"
echo "6 - Registry-Datei aktualisieren"
echo "8 - Lösche den Container und die Daten des Projekts"
echo "9 - Hard Reset (alles löschen und neu erstellen)"
echo "0 - Beenden"

read -p "Eingabe: " choice
case $choice in
    1)
        log "$PROJECT_NAME" "Erstelle config.json Datei..."
        # Führe das create_database.sh-Skript aus
        bash "$CREATE_DB_SCRIPT"
        connect_network
        create_config_json
        # Initialisiere das Projekt
        log "$PROJECT_NAME" "Starte Datenbankerstellung und Initialisierung..."
        initialize_project
        ;;
    2)
        log "$PROJECT_NAME" "Erstelle config.json Datei..."
        create_config_json
        ;;
    3)
        log "$PROJECT_NAME" "Starten oder Neustarten des Docker-Containers..."
        cd "$COMPOSE_DIR"
        docker-compose up -d
        log "$PROJECT_NAME" "Erstelle config.json Datei nach dem Starten des Containers..."
        create_config_json
        connect_network
        ;;
    5)
        log "$PROJECT_NAME" "Stoppen des Docker-Containers..."
        cd "$COMPOSE_DIR"
        docker-compose down
        ;;
    6)
        log "$PROJECT_NAME" "Aktualisiere Registry-Datei..."
        initialize_project
        ;;
    8)
        echo -e "\e[41m\e[97mWARNUNG: Dies wird den Container und alle Daten des Projekts löschen!\e[0m"
        read -p "Möchtest du wirklich fortfahren? (yes/no): " confirmation
        if [ "$confirmation" == "yes" ]; then
            log "$PROJECT_NAME" "Lösche den Container und die Daten des Projekts..."
            cd "$COMPOSE_DIR"
            docker-compose down -v  # -v entfernt auch die Volumes
            delete_all_databases
            log "$PROJECT_NAME" "Container und Daten wurden erfolgreich gelöscht."
        else
            log "$PROJECT_NAME" "Löschung des Containers und der Daten abgebrochen."
        fi
        ;;
    9)
        echo -e "\e[41m\e[97mWARNUNG: Dies wird den Container und alle Daten des Projekts löschen!\e[0m"
        read -p "Möchtest du wirklich fortfahren? (yes/no): " confirmation
        if [ "$confirmation" == "yes" ]; then
            log "$PROJECT_NAME" "Hard Reset wird durchgeführt..."
            cd "$COMPOSE_DIR"
            docker-compose down -v  # -v entfernt auch die Volumes
            delete_all_databases
            log "$PROJECT_NAME" "Container und Daten wurden erfolgreich gelöscht."
            log "$PROJECT_NAME" "Lösche alte config.json Datei..."
            delete_config_json
            log "$PROJECT_NAME" "Erstelle neue config.json Datei..."
            create_config_json
            bash "$CREATE_DB_SCRIPT"
            # Initialisiere das Projekt
            initialize_project
            docker-compose up -d
            log "$PROJECT_NAME" "Erstelle config.json Datei nach dem Starten des Containers..."
            create_config_json
            connect_network
        else
            log "$PROJECT_NAME" "Hard Reset abgebrochen."
        fi
        ;;
    0)
        echo "Beenden..."
        exit 0
        ;;
    *)
        echo "Ungültige Eingabe. Bitte wähle eine gültige Option."
        ;;
esac