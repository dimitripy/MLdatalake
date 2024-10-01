# MLdatalake

## Übersicht

Dieses Projekt verwaltet eine MySQL-Datenbank für MLdatalake. Das `control_center.sh` Skript bietet verschiedene Funktionen zur Verwaltung der Datenbank und der Docker-Container.

## .env Datei

Die `.env` Datei enthält die Umgebungsvariablen, die für die Konfiguration der MySQL-Datenbank und anderer Dienste erforderlich sind. Diese Datei sollte im Stammverzeichnis des Projekts erstellt werden und wird aus Sicherheitsgründen im `.gitignore` ausgeblendet.

## Beispiel `.env` Datei

Erstelle eine `.env` Datei mit folgendem Inhalt:

```env
# MySQL Datenbankkonfiguration
MYSQL_ROOT_PASSWORD=mysecretpassword
MYSQL_DATABASE=mldatalake
MYSQL_USER=mldatalake_user
MYSQL_PASSWORD=userpassword
```


- MYSQL_ROOT_PASSWORD: Das Passwort für den MySQL-Root-Benutzer.
- MYSQL_DATABASE: Der Name der MySQL-Datenbank, die erstellt werden soll.
- MYSQL_USER: Der Benutzername für den MySQL-Benutzer.
- MYSQL_PASSWORD: Das Passwort für den MySQL-Benutzer.



## Funktionen des control_center.sh Skripts
Das control_center.sh Skript bietet ein Menü zur Verwaltung der MySQL-Datenbank und der Docker-Container. Hier sind die verfügbaren Optionen:

1. Datenbank erstellen und initialisieren
Diese Option startet das create_database.sh Skript, das die MySQL-Datenbank erstellt und initialisiert.

2. config.json Datei erstellen
Diese Option erstellt eine config.json Datei mit den Datenbankkonfigurationswerten aus der .env Datei.

3. Starten oder Neustarten des Docker-Containers
Diese Option startet oder startet die Docker-Container neu, die in der docker-compose.yml Datei definiert sind.

5. Stoppen des Docker-Containers
Diese Option stoppt die Docker-Container, die in der docker-compose.yml Datei definiert sind.

8. Lösche den Container und die Daten des Projekts
Diese Option löscht die Docker-Container und alle zugehörigen Daten. Eine Bestätigung ist erforderlich, um fortzufahren.

9. Hard Reset (alles löschen und neu erstellen)
Diese Option führt einen Hard Reset durch, bei dem die Docker-Container und alle zugehörigen Daten gelöscht und neu erstellt werden.

0. Beenden
Diese Option beendet das Skript.

## Verwendung
Erstelle die .env Datei im Stammverzeichnis des Projekts.
Führe das control_center.sh Skript aus:
Wähle die gewünschte Option aus dem Menü.
Beispiel
Lizenz
Dieses Projekt ist unter der MIT-Lizenz lizenziert. Weitere Informationen findest du in der LICENSE Datei.