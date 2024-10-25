import os
import shutil
from google.colab import drive

# Mount Google Drive
drive.mount('/content/drive')

# Lokalen Datenbankpfad und Zielpfad auf Google Drive definieren
local_db_path = '/path/to/your/crypto_data.db'
drive_db_path = '/content/drive/MyDrive/crypto_data.db'

# Datenbank synchronisieren
shutil.copyfile(local_db_path, drive_db_path)
