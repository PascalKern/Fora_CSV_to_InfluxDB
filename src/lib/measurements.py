import dataclasses
import math
from dataclasses import dataclass
from datetime import datetime
from typing import List, Any

from lib.constants import MeasurementUnit, Period
from lib.process_csv import ForaMedicalRecord


@dataclass(frozen=True)
class BaseMeasurement(object):
    date_time: datetime
    note: str
    unit: MeasurementUnit
    value: float
    period: Period = Period.EMPTY
    measurement_type: str = dataclasses.field(init=False)

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
    measurement_type = 'blood_glucose'


@dataclass(frozen=True)
class Hematocrit(BaseMeasurement):
    measurement_type = 'hematocrit'


@dataclass(frozen=True)
class Hemoglobin(BaseMeasurement):
    measurement_type = 'hemoglobin'


# TODO Need's calc depending on hematocrit unit?! Think not as hematocrit is in percentage but
#  percentage of? g/dl or mmol/L
# TODO Maybe move into the Hematologic measurement class! Would make bellow swich simpler and not require
#  the record to be passed in as well?!
def _calc_hemoglobine(record):
    hematocrit_value = record.get_measurement_by_name('hematocrit_perc')
    # Calculation from Android App code: FLOOR('Hematocrit(%)' × 0.340000003576279 × 10,1) ÷ 10
    HEMOTACRIT_TO_HEMOGLOBINE = 0.340000003576279
    return math.floor(hematocrit_value * HEMOTACRIT_TO_HEMOGLOBINE * 10) / 10


@dataclass(frozen=True)
class Ketnone(BaseMeasurement):
    measurement_type = 'ketone'


@dataclass(frozen=True)
class Chloresterol(BaseMeasurement):
    measurement_type = 'cholesterol'


@dataclass(frozen=True)
class UricAcid(BaseMeasurement):
    measurement_type = 'uric_acid'


@dataclass(frozen=True)
class Triglycerides(BaseMeasurement):
    measurement_type = 'triglycerides'


@dataclass(frozen=True)
class Lactate(BaseMeasurement):
    measurement_type = 'lactate'


def _build_measurement(measurement: str, value: float, record: ForaMedicalRecord) -> List[BaseMeasurement]:
    date_time = record.get_date_time()
    period = record.get_period()
    note = record.get_note()

    meas_unit = MeasurementUnit.get_unit_for_csv_header_name(measurement)
    meas_type = measurement.replace('_' + meas_unit.get_csv_header_format(), '')
    match meas_type:
        case 'hematocrit':
            cal_value = _calc_hemoglobine(record)
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
            raise ValueError(f'Unexpected measurement type: {measurement}')
    return Any


def convert_record_to_measurement(record: ForaMedicalRecord) -> List[BaseMeasurement]:
    res: List[BaseMeasurement] = []
    for measurement, value in record.get_measurement_with_values():
        res.extend(_build_measurement(measurement, value, record))
    return res
