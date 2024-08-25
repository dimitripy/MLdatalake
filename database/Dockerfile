# Verwende ein offizielles Python-Image als Basis
FROM python:3.9-slim

# Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere die Anforderungen in den Container
COPY requirements.txt requirements.txt

# Installiere die Python-Abhängigkeiten
RUN pip install -r requirements.txt

# Kopiere den restlichen Quellcode in das Arbeitsverzeichnis
COPY . .

# Starte das Python-Skript
CMD ["python", "your_script.py"]
