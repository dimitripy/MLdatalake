#!/bin/bash
# control_center.sh - Skript zur Verwaltung von MLdatalake

# Gemeinsame Funktionen einbinden
source "$(dirname "${BASH_SOURCE[0]}")/comms/common_functions.sh"

# Verzeichnisse und Dateien definieren
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_DIR="$SCRIPT_DIR/mldatalake"  # Verzeichnis mit der docker-compose.yml
ENV_FILE="$SCRIPT_DIR/.env"  # Pfad zur .env Datei
CONFIG_FILE="$SCRIPT_DIR/dags/latest/config.json"  # Pfad zur config.json Datei

# Definiere den Projektnamen für das Logging
PROJECT_NAME="mldatalake"

# Lade die Umgebungsvariablen aus der .env Datei
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo "Fehler: Die .env Datei wurde nicht gefunden."
    exit 1
fi

# Funktion zum Erstellen der config.json Datei
create_config_json() {
    cat <<EOF > "$CONFIG_FILE"
{
    "db_user": "$MYSQL_USER",
    "db_password": "$MYSQL_PASSWORD",
    "db_host": "localhost",
    "db_name": "$MYSQL_DATABASE"
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

# Menü für Benutzerinteraktion
echo "Bitte wähle eine Option:"
echo "1 - Datenbank erstellen und initialisieren"
echo "2 - config.json Datei erstellen"
echo "3 - Starten oder Neustarten des Docker-Containers"
echo "5 - Stoppen des Docker-Containers"
echo "8 - Lösche den Container und die Daten des Projekts"
echo "9 - Hard Reset (alles löschen und neu erstellen)"
echo "0 - Beenden"

read -p "Eingabe: " choice
case $choice in
    1)
        log "$PROJECT_NAME" "Erstelle config.json Datei..."
        create_config_json
        log "$PROJECT_NAME" "Starte Datenbankerstellung und Initialisierung..."
        # Führe das create_database.sh-Skript aus
        bash "$SCRIPT_DIR/customs/create_database.sh"
        ;;
    2)
        log "$PROJECT_NAME" "Erstelle config.json Datei..."
        create_config_json
        ;;
    3)
        log "$PROJECT_NAME" "Starten oder Neustarten des Docker-Containers..."
        cd "$COMPOSE_DIR"
        docker-compose up -d
        ;;
    5)
        log "$PROJECT_NAME" "Stoppen des Docker-Containers..."
        cd "$COMPOSE_DIR"
        docker-compose down
        ;;
    8)
        echo -e "\e[41m\e[97mWARNUNG: Dies wird den Container und alle Daten des Projekts löschen!\e[0m"
        read -p "Möchtest du wirklich fortfahren? (yes/no): " confirmation
        if [ "$confirmation" == "yes" ]; then
            log "$PROJECT_NAME" "Lösche den Container und die Daten des Projekts..."
            cd "$COMPOSE_DIR"
            docker-compose down -v  # -v entfernt auch die Volumes
            log "$PROJECT_NAME" "Container und Daten wurden erfolgreich gelöscht."
        else
            log "$PROJECT_NAME" "Löschung des Containers und der Daten abgebrochen."
        fi
        ;;
    9)
        log "$PROJECT_NAME" "Hard Reset wird durchgeführt..."
        cd "$COMPOSE_DIR"
        docker-compose down -v
        log "$PROJECT_NAME" "Lösche alte config.json Datei..."
        delete_config_json
        log "$PROJECT_NAME" "Erstelle neue config.json Datei..."
        create_config_json
        bash "$SCRIPT_DIR/customs/create_database.sh"
        docker-compose up -d
        ;;
    0)
        echo "Beenden..."
        exit 0
        ;;
    *)
        echo "Ungültige Eingabe. Bitte wähle eine gültige Option."
        ;;
esac