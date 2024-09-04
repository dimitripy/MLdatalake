#!/bin/bash
# manage_database.sh - Skript zur Verwaltung der MySQL-Datenbank ohne Docker Compose

# Gemeinsame Funktionen einbinden
source "$(dirname "${BASH_SOURCE[0]}")/Comms/common_functions.sh"

# Verzeichnisse und Dateien definieren
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOST_DB_PATH="$SCRIPT_DIR/../database_data"
CREATE_DB_SCRIPT="$SCRIPT_DIR/create_database.sh"  # Pfad zum create_database.sh Skript
IMAGE_NAME="my-mysql-db"
CONTAINER_NAME="my-mysql-container"
ENV_FILE="$SCRIPT_DIR/.env"  # Pfad zur .env Datei

# Definiere den Projektnamen für das Logging
PROJECT_NAME="mldatalake"

# Sicherstellen, dass das Datenverzeichnis existiert
mkdir -p "$HOST_DB_PATH"

# Erstelle die .env Datei, falls sie nicht existiert
if [ ! -f "$ENV_FILE" ]; then
    echo "Erstelle .env Datei mit Standardwerten..."
    cat <<EOL > "$ENV_FILE"
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=mydatabase
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_PORT=3306
MYSQL_HOST=localhost
EOL
    echo ".env Datei wurde erstellt."
fi

# Lade die Umgebungsvariablen aus der .env Datei
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo "Fehler: Die .env Datei wurde nicht gefunden."
    exit 1
fi

# Überprüfe, ob die benötigten Umgebungsvariablen gesetzt sind
REQUIRED_VARS=("MYSQL_ROOT_PASSWORD" "MYSQL_DATABASE" "MYSQL_USER" "MYSQL_PASSWORD" "MYSQL_PORT")

for VAR in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!VAR}" ]; then
        echo "Fehler: Die Umgebungsvariable $VAR ist nicht gesetzt. Bitte überprüfe die .env Datei."
        exit 1
    fi
done

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

        # Baue das Docker-Image für MySQL
        echo "Baue das Docker-Image für MySQL..."
        docker build -t $IMAGE_NAME ./mldatalake

        # Starte den MySQL-Container mit den Umgebungsvariablen aus der .env Datei
        echo "Starte den MySQL-Container..."
        docker run -d \
          --name $CONTAINER_NAME \
          -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD \
          -e MYSQL_DATABASE=$MYSQL_DATABASE \
          -e MYSQL_USER=$MYSQL_USER \
          -e MYSQL_PASSWORD=$MYSQL_PASSWORD \
          -v "$HOST_DB_PATH":/var/lib/mysql \
          -p $MYSQL_PORT:3306 \
          $IMAGE_NAME

        # Warte auf den MySQL-Container und prüfe bis zu 8 Versuche, ob er läuft
        MAX_ATTEMPTS=8
        ATTEMPT=1

        while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
            echo "Warte auf MySQL-Container... Versuch $ATTEMPT von $MAX_ATTEMPTS"
            sleep 5

            # Prüfe, ob der Container läuft
            if [ "$(docker inspect -f '{{.State.Running}}' $CONTAINER_NAME)" = "true" ]; then
                echo "MySQL-Container läuft erfolgreich."
                break
            fi

            ATTEMPT=$((ATTEMPT + 1))
        done

        # Falls der Container nach allen Versuchen nicht gestartet ist, Fehler melden
        if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
            echo "Fehler: MySQL-Container konnte nach $MAX_ATTEMPTS Versuchen nicht gestartet werden."
            exit 1
        fi

        # Führe das create_database.sh Skript zur Initialisierung der Datenbank aus
        if [ -f "$CREATE_DB_SCRIPT" ]; then
            bash "$CREATE_DB_SCRIPT"
            log "$PROJECT_NAME" "Datenbankerstellung und Initialisierung abgeschlossen."
        else
            log "$PROJECT_NAME" "Fehler: Das Skript $CREATE_DB_SCRIPT wurde nicht gefunden."
        fi
        ;;
    3)
        log "$PROJECT_NAME" "Starten oder Neustarten des Docker-Containers..."
        # Überprüfe, ob der Container existiert
        if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
            # Wenn der Container gestoppt ist, starte ihn
            if [ "$(docker inspect -f '{{.State.Running}}' $CONTAINER_NAME)" = "false" ]; then
                docker start $CONTAINER_NAME
                echo "Docker-Container $CONTAINER_NAME wurde gestartet."
            else
                # Wenn der Container läuft, starte ihn neu
                docker restart $CONTAINER_NAME
                echo "Docker-Container $CONTAINER_NAME wurde neu gestartet."
            fi
        else
            echo "Container $CONTAINER_NAME existiert nicht. Bitte wähle Option 1, um den Container zu erstellen."
        fi
        ;;
    5)
        log "$PROJECT_NAME" "Stoppen des Docker-Containers..."
        if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
            docker stop $CONTAINER_NAME
            echo "Docker-Container $CONTAINER_NAME wurde gestoppt."
        else
            echo "Der Container $CONTAINER_NAME läuft nicht oder existiert nicht."
        fi
        ;;
    8)
        echo -e "\e[41m\e[97mWARNUNG: Dies wird den Container und alle Daten des Projekts löschen!\e[0m"
        read -p "Möchtest du wirklich fortfahren? (yes/no): " confirmation
        if [ "$confirmation" == "yes" ]; then
            log "$PROJECT_NAME" "Lösche den Container und die Daten des Projekts..."
            docker stop $CONTAINER_NAME
            docker rm $CONTAINER_NAME
            rm -rf "$HOST_DB_PATH"
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
            docker stop $CONTAINER_NAME
            docker rm $CONTAINER_NAME
            rm -rf "$HOST_DB_PATH"
            bash "$0"  # Neustart des Skripts, um die Umgebung neu zu erstellen
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