import dataclasses
import math
from dataclasses import dataclass
from datetime import datetime
from typing import List

from lib.constants import MeasurementUnit, Period, HEMATOCRIT_TO_HEMOGLOBIN
from lib.process_csv import ForaMedicalRecord, ForaMedicalRecords


@dataclass(frozen=True)
class BaseMeasurement(object):
    date_time: datetime                 # "key" aka Timeseries-PrimaryKey
    note: str                           #
    unit: MeasurementUnit
    value: float
    period: Period = Period.EMPTY
    measurement_name: str = dataclasses.field(init=False)
    default_unit: MeasurementUnit = dataclasses.field(init=False)

    def _items(self):
        for cls_field in dataclasses.fields(self):
            yield cls_field.name, getattr(self, cls_field.name)

    def __str__(self):
        res = ''
        for k, v in self._items():
            import os
            res += f'{k:<24} -> {v}{os.linesep}'
        return res.strip()


@dataclass(frozen=True)
class BloodGlucose(BaseMeasurement):
    measurement_name = 'blood_glucose'
    default_unit = MeasurementUnit.MG_DL


@dataclass(frozen=True)
class Hematocrit(BaseMeasurement):
    measurement_name = 'hematocrit'
    default_unit = MeasurementUnit.PERCENTAGE


@dataclass(frozen=True)
class Hemoglobin(BaseMeasurement):
    measurement_name = 'hemoglobin'
    default_unit = MeasurementUnit.G_DL


@dataclass(frozen=True)
class Ketnone(BaseMeasurement):
    measurement_name = 'ketone'
    default_unit = MeasurementUnit.MMOL_L


@dataclass(frozen=True)
class Chloresterol(BaseMeasurement):
    measurement_name = 'cholesterol'
    default_unit = MeasurementUnit.MG_DL


@dataclass(frozen=True)
class UricAcid(BaseMeasurement):
    measurement_name = 'uric_acid'
    default_unit = MeasurementUnit.MG_DL


@dataclass(frozen=True)
class Triglycerides(BaseMeasurement):
    measurement_name = 'triglycerides'
    default_unit = MeasurementUnit.MG_DL


@dataclass(frozen=True)
class Lactate(BaseMeasurement):
    measurement_name = 'lactate'
    default_unit = MeasurementUnit.MMOL_L

# TODO Need's calc depending on hematocrit unit?! Think not as hematocrit is in percentage but
#  percentage of? g/dl or mmol/L
# TODO Maybe move into the Hematologic measurement class! Would make bellow swich simpler and not require
#  the record to be passed in as well?!
def _calc_hemoglobine(hematocrit_value: float) -> float:
    # Calculation from Android App code: FLOOR('Hematocrit(%)' × 0.340000003576279 × 10,1) ÷ 10
    return math.floor(hematocrit_value * HEMATOCRIT_TO_HEMOGLOBIN * 10) / 10

def _build_measurement(meas_type: str, value: float, meas_unit: MeasurementUnit, record: ForaMedicalRecord) -> List[BaseMeasurement]:
    date_time = record.get_date_time()
    period = record.get_period()
    note = record.get_note()

    match meas_type:
        case 'hematocrit':
            cal_value = _calc_hemoglobine(value)
            return [Hemoglobin(date_time=date_time, note=note, unit=meas_unit, value=cal_value, period=period),
                    Hematocrit(date_time=date_time, note=note, unit=meas_unit, value=value, period=period)]
        case 'blood_glucose':
            return [BloodGlucose(date_time=date_time, note=note, unit=meas_unit, value=value, period=period)]
        case 'ketone':
            return [Ketnone(date_time=date_time, note=note, unit=meas_unit, value=value, period=period)]
        case 'cholesterol':
            return [Chloresterol(date_time=date_time, note=note, unit=meas_unit, value=value, period=period)]
        case 'uric_acid':
            return [UricAcid(date_time=date_time, note=note, unit=meas_unit, value=value, period=period)]
        case 'triglycerides':
            return [Triglycerides(date_time=date_time, note=note, unit=meas_unit, value=value, period=period)]
        case 'lactate':
            return [Lactate(date_time=date_time, note=note, unit=meas_unit, value=value, period=period)]
        case _:
            raise ValueError(f'Unexpected measurement type: {meas_type}')


def convert_record_to_measurement(record: ForaMedicalRecord) -> List[BaseMeasurement]:
    res: List[BaseMeasurement] = []
    for measurement, value in record.get_measurements_and_values():
        meas_unit = MeasurementUnit.get_unit_from_csv_header(measurement)
        meas_type = measurement.replace('_' + meas_unit.get_medical_record_unit(), '')
        res.extend(_build_measurement(meas_type, value, meas_unit, record))
    return res


def convert_records_to_measurements(records: ForaMedicalRecords) -> List[BaseMeasurement]:
    res: List[BaseMeasurement] = []
    for record in records:
        for measurement, value in record.get_measurements_and_values():
            res.extend(_build_measurement(measurement, value, record))
    return res
