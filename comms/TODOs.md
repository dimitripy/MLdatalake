# Anleitung zur Erstellung und Verwendung einer zentralen Library

Diese Anleitung beschreibt, wie du ein zentrales Repository für gemeinsame Module erstellst und diese in mehreren Projekten verwendest.

## Schritt 1: Erstelle ein zentrales Repository

1. Gehe zu GitHub und erstelle ein neues Repository, z.B. `common-library`.
2. Füge deine gemeinsamen Module in dieses Repository ein.

## Schritt 2: Füge das zentrale Repository als Submodul zu deinen Projekten hinzu

1. Navigiere zu deinem Projektverzeichnis.
2. Füge das zentrale Repository als Submodul hinzu:
   ```bash
   git submodule add https://github.com/dein-benutzername/common-library.git lib
   ```

3. Initialisiere und aktualisiere das Submodul
   ```bash
    git submodule update --init --recursive
   ```

## Schritt 3: Verwende die Library in deinem Projekt
Beispiel für die Verwendung in einem Bash-Skript
Angenommen, du hast ein gemeinsames Modul registry.sh im Verzeichnis lib, das du in deinem Projekt verwenden möchtest:
```bash
#!/bin/bash
# main.sh

# Importiere das gemeinsame Modul
source lib/registry.sh

# Verwende die Funktionen aus dem gemeinsamen Modul
register_in_registry "mein_projekt" dag_path="/pfad/zu/dag"

```
Beispiel für die Verwendung in einer Python-Datei
Angenommen, du hast ein gemeinsames Modul common.py im Verzeichnis lib, das du in deinem Projekt verwenden möchtest:


```python
# main.py

# Importiere das gemeinsame Modul
import sys
sys.path.insert(0, 'lib')

import common

# Verwende die Funktionen aus dem gemeinsamen Modul
common.some_function()
```

## Schritt 4: Aktualisiere das Submodul bei Änderungen
Wenn du Änderungen an der Library im zentralen Repository vornimmst, kannst du diese Änderungen in deinen Projekten aktualisieren:

cd lib
git pull origin main
cd ..
git add lib
git commit -m "Aktualisiere gemeinsame Library"
git push