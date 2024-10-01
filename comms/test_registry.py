#eventuell braucht man das nicht mehr oder bei der Umstellung auf python noch

import yaml
from collections import defaultdict

registry_file = '/etc/airflow/airflow_dag_registry.yaml'
project_name = 'mldatalake'
key = 'dag_path'
value = '/home/ageq/Git_Projects/MLdatalake/dags'

print(f'Öffne Datei: {registry_file}')
with open(registry_file, 'r') as file:
    data = yaml.safe_load(file) or {'projects': defaultdict(dict)}

print(f'Aktualisiere Projekt: {project_name} mit {key}={value}')
data['projects'].setdefault(project_name, {})[key] = value

print(f'Speichere Datei: {registry_file}')
with open(registry_file, 'w') as file:
    yaml.safe_dump(data, file)