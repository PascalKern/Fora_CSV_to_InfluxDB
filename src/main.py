# This is a sample Python script.
import argparse
import os
from pathlib import Path

from lib.measurements import convert_record_to_measurement
from lib.process_csv import ForaMedicalRecords

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A tool to convert and send content to influxdb the "
                                                 "iFora HM App exported csv")
    parser.add_argument('-c', '--csv', type=Path, required=True, help='Path to the csv file')

    args = parser.parse_args()

    full_records = ForaMedicalRecords.from_csv_file(args.csv)

    print(f'{"All Medical Records":-^64}')
    print(full_records)
    print(f'{"First Medical Record":-^64}')
    print(full_records.get_record(0))

    print(f'{"Iterate Med. Record Holder":-^64}')
    test = True
    for record in full_records:
        if test:
            print(record)
            test = False
            break
    print(f'{"Get First Med. Rec. Measurements":-^64}')
    print(full_records.get_record(0).get_measurements_and_values())
    print(f'{"Created Measurements from Med. Rec.":-^64}')
    measurements = convert_record_to_measurement(full_records.get_record(0))
    print(measurements)
    print(f'{"Single Measurements":-^64}')
    for measurement in measurements:
        print(f'{measurement}{os.linesep}')
