import os
import subprocess
from airflow.exceptions import AirflowException

# Datenbank-Backup erstellen
def create_db_backup():
    backup_dir = "/path/to/backup"  # Backup-Verzeichnis
    backup_file = os.path.join(backup_dir, 'db_backup.sql')
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    command = f"mysqldump -u {db_user} -p{db_password} -h {db_host} {db_name} > {backup_file}"
    
    try:
        # Das Backup ausführen und den Status überwachen
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Datenbank-Backup erfolgreich gespeichert unter: {backup_file}")
        return backup_file
    except subprocess.CalledProcessError as e:
        # Wenn der Prozess einen Fehler wirft, eine AirflowException auslösen
        print(f"Fehler beim Erstellen des Datenbank-Backups: {e.stderr.decode('utf-8')}")
        raise AirflowException(f"Backup-Prozess fehlgeschlagen: {e}")
