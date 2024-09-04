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