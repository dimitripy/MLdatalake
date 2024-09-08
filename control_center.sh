#!/bin/bash
# control_center.sh - Skript zur Verwaltung von MLdatalake

# Gemeinsame Funktionen einbinden
source "$(dirname "${BASH_SOURCE[0]}")/Comms/common_functions.sh"

# Verzeichnisse und Dateien definieren
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_DIR="$SCRIPT_DIR/../"  # Verzeichnis mit der docker-compose.yml
ENV_FILE="$SCRIPT_DIR/.env"  # Pfad zur .env Datei

# Definiere den Projektnamen für das Logging
PROJECT_NAME="mldatalake"

# Lade die Umgebungsvariablen aus der .env Datei
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo "Fehler: Die .env Datei wurde nicht gefunden."
    exit 1
fi

# Menü für Benutzerinteraktion
echo "Bitte wähle eine Option:"
echo "1 - Datenbank erstellen und initialisieren"
echo "3 - Starten oder Neustarten des Docker-Containers"
echo "5 - Stoppen des Docker-Containers"
echo "8 - Lösche den Container und die Daten des Projekts"
echo "9 - Hard Reset (alles löschen und neu erstellen)"
echo "0 - Beenden"

read -p "Eingabe: " choice
case $choice in
    1)
        log "$PROJECT_NAME" "Starte Datenbankerstellung und Initialisierung..."
        # Führe das create_database.sh-Skript aus
        bash "$SCRIPT_DIR/scripts/create_database.sh"
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
        echo -e "\e[41m\e[97mWARNUNG: Dies wird ALLE Dateien und Verzeichnisse löschen und neu erstellen!\e[0m"
        read -p "Möchtest du wirklich fortfahren? (yes/no): " confirmation
        if [ "$confirmation" == "yes" ]; then
            log "$PROJECT_NAME" "Führe Hard Reset durch..."
            cd "$COMPOSE_DIR"
            docker-compose down -v
            bash "$SCRIPT_DIR/scripts/create_database.sh"
        else
            log "$PROJECT_NAME" "Hard Reset vom Benutzer abgebrochen."
        fi
        ;;
    0)
        log "$PROJECT_NAME" "Beenden ohne Änderungen."
        exit 0
        ;;
    *)
        echo "Ungültige Auswahl. Bitte 1, 3, 5, 8, 9 oder 0 wählen."
        ;;
esac
