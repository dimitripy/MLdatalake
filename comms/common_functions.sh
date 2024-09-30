#!/bin/bash

# log() Funktion mit dynamischem Log-Verzeichnis
log() {
    local project_name="$1"
    local message="$2"

    # Erstelle ein Log-Verzeichnis basierend auf dem Projektnamen
    local log_dir="$(pwd)/logs/$project_name"
    mkdir -p "$log_dir"

    # Setze den Log-Dateipfad basierend auf dem Projektnamen
    local log_file="$log_dir/${project_name}_restart.log"

    # Schreibe die Nachricht in die Log-Datei
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $message" | tee -a "$log_file"
}

# Docker-Container und Volumes bereinigen (nur die des aktuellen Projekts)
cleanup_containers_and_volumes() {
    local compose_file="$1"
    local data_dir="$2"
    local project_name="$3"  # Projektnamen als Argument hinzufügen

    if [ -f "$compose_file" ]; then
        log "$project_name" "Shutting down and removing Docker containers and volumes for the current project..."

        # Setze den COMPOSE_PROJECT_NAME auf den Basisnamen des Verzeichnisses
        export COMPOSE_PROJECT_NAME="$project_name"

        # Stoppe und entferne nur die Container und Volumes des aktuellen Projekts
        sudo docker-compose -f "$compose_file" down --volumes --remove-orphans

        log "$project_name" "Docker containers and volumes for $COMPOSE_PROJECT_NAME removed successfully"

        # MySQL-Datenverzeichnis löschen, falls angegeben
        if [ -n "$data_dir" ] && [ -d "$data_dir" ]; then
            log "$project_name" "Removing MySQL data directory at $data_dir..."
            sudo rm -rf "$data_dir"
            log "$project_name" "MySQL data directory removed successfully"
        else
            log "$project_name" "MySQL data directory not found or already removed."
        fi
    else
        log "$project_name" "docker-compose.yml not found, skipping Docker cleanup"
    fi
}

# Docker-Container neustarten
restart_docker_containers() {
    local compose_file="$1"
    local project_name="$2"  # Projektnamen als Argument hinzufügen

    log "$project_name" "Starting Docker containers using docker-compose..."

    # Setze den COMPOSE_PROJECT_NAME auf den Basisnamen des Verzeichnisses
    export COMPOSE_PROJECT_NAME="$project_name"

    sudo docker-compose -f "$compose_file" up -d
    log "$project_name" "Docker containers for $COMPOSE_PROJECT_NAME started successfully"
}