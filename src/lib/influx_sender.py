import os
from datetime import datetime

from influxdb import InfluxDBClient

from influxdb_client import InfluxDBClient as InfluxDBClientV2
from influxdb_client import Point
from influxdb_client.domain.script_create_request import ScriptCreateRequest
from influxdb_client.domain.script_language import ScriptLanguage

import config
from lib.measurements import BaseMeasurement


def _creat_client_w_token() -> InfluxDBClient:
    # Can be used for InfluxQL queries but might be tricky to write data properly with this client!
    client = InfluxDBClient(
        host = config.INFLUXDB_HOST,
        port = config.INFLUXDB_PORT,
        username = None,
        password = None,
        headers = {"Authorization": f'Token {config.INFLUXDB_TOKEN}'},
        database = config.INFLUX_BUCKET
    )
    return client


def _create_client_v2_lib_w_token() -> InfluxDBClientV2:
    # Can be used (for sure) to execute flux queries but maybe only maybe also for influxQL!
    client = InfluxDBClientV2(
        url=f'http://{config.INFLUXDB_HOST}:{config.INFLUXDB_PORT}',
        token=config.INFLUXDB_TOKEN, # Maybe would work with _ALL ?!
        org=config.INFLUXDB_ORG,
    )
    return client

def _try_v2_lib_influxql_query(client: InfluxDBClientV2):
    script_create_request = ScriptCreateRequest(
        name=f'my_script_{str(datetime.now())}',
        description='My test Script',
        language=ScriptLanguage.INFLUXQL,
        script='SHOW DATABASES'
    )

    scripts_api = client.invokable_scripts_api()
    script = scripts_api.create_script(script_create_request)
    print(f'Script:{os.linesep}{script}')


# TODO Next to be implemented! Using experiments / tries in this file and create a proper class
#  ie. InfluxClient (most likely the correct class and name!) / MeasurementToPoint[Handler] / DataPoint[Handler/Manager] / ...
#  Maybe more classes needed for a "nice" / clean design
def _build_datapoint_from_measurement(measurement: BaseMeasurement) -> Point:
    raise BaseException('Not yet implemented')


def _check_datapoint_does_not_yet_exist(datapoint: Point) -> bool:
    raise BaseException('Not yet implemented')


def _get_latest_datapoint_timestamp() -> datetime:
    raise BaseException('Not yet implemented')



if __name__ == '__main__':
    client = _creat_client_w_token()
    print(f'DB Version: {client.ping()}')
    print(f'DB\'s: {client.get_list_database()}')

    client_v2 = _create_client_v2_lib_w_token()
    print(f'DB Version: {client_v2.ping()}')
    print(f'Health: {client_v2.health()}')
    # _try_v2_lib_influxql_query(client_v2) # Seems to only work in Cloud!

    p = Point('test_meas_blood').tag('device', 'fora 6 connect').field('hematocrit', 14.4)
    print(f'Point: {p}')
    print(f'Point as line protocol: {p.to_line_protocol()}')
