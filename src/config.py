
from dotenv import dotenv_values

envs = dotenv_values('.devcontainer/.env', verbose=True)

INFLUXDB_HOST = envs.get('INFLUXDB_HOST', 'rock-4c-plus')
INFLUXDB_PORT = envs.get('INFLUXDB_PORT', 8086)
INFLUXDB_ORG = envs.get('INFLUXDB_ORG', 'info.pkern.health')
INFLUX_BUCKET = envs.get('INFLUX_BUCKET', 'blood_ifora_hm')
INFLUXDB_USER = envs.get('INFLUXDB_USER', 'admin')
INFLUXDB_TOKEN = envs.get('INFLUXDB_TOKEN', 'WSSzunUrKe8keVE-NT950Lwfs6u-m03VnQ==')
