#Stand: ist No 1 in works_v2

# zip_extractor.py
import os
from zipfile import ZipFile
import json  # Für das Einlesen der Konfiguration, wenn af nicht verfügbar

def extract_zip(zip_file_path, extract_to_path):
    """Entpackt eine ZIP-Datei in das angegebene Verzeichnis."""
    with ZipFile(zip_file_path, 'r') as zf:
        zf.extractall(extract_to_path)
    print(f"ZIP-Datei wurde erfolgreich nach {extract_to_path} entpackt.")

def load_config(config_path):
    """Lädt eine Konfigurationsdatei im JSON-Format."""
    with open(config_path, 'r') as f:
        return json.load(f)

def main_extract_zip(config_path='config.json', source_path='/home/ageq/Git_Projects/MLdatalake/source'):
    """Hauptfunktion zum Laden der Konfiguration und Entpacken der ZIP-Datei."""
    try:
        config = load_config(config_path)
        zip_file_name = config['zip_file_name']
        
        # Erstellen des vollständigen Pfades zur ZIP-Datei
        zip_file_path = os.path.join(source_path, f"{zip_file_name}.zip")
        extract_to_path = os.path.join(source_path, zip_file_name)
        
        # Entpacken der ZIP-Datei
        extract_zip(zip_file_path, extract_to_path)
    except Exception as e:
        print(f"An error occurred: {e}")

# main_extract_zip kann nun direkt als Modul verwendet werden
