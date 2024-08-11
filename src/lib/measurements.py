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
    period: Period = Period.EMPTY


@dataclass(frozen=True)
class Hematocrit(BaseMeasurement):
    measurement_type = 'hematocrit'
    period: Period = Period.EMPTY


@dataclass(frozen=True)
class Hemoglobin(BaseMeasurement):
    measurement_type = 'hemoglobin'
    period: Period = Period.EMPTY


# TODO Need's calc depending on hematocrit unit?! Think not as hematocrit is in percentage but
#  percentage of? g/dl or mmol/L
def _calc_hemoglobine(record):
    hematocrit_value = record.get_measurement_by_name('hematocrit_perc')
    # Calculation from Android App code: FLOOR('Hematocrit(%)' × 0.340000003576279 × 10,1) ÷ 10
    HEMOTACRIT_TO_HEMOGLOBINE = 0.340000003576279
    return math.floor(hematocrit_value * HEMOTACRIT_TO_HEMOGLOBINE * 10) / 10


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
        case 'ketone_mmol':
            pass
        case 'ketone_mg_dl':
            pass
        case 'cholesterol_mg_dl':
            pass
        case 'cholesterol_mmol':
            pass
        case 'uric_acid_mg':
            pass
        case 'uric_acid_umol':
            pass
        case 'uric_acid_mmol':
            pass
        case 'triglycerides_mg_dl':
            pass
        case 'triglycerides_mmol':
            pass
        case 'lactate_mmol':
            pass
        case _:
            raise ValueError(f'Unexpected measurement type: {measurement}')
    return Any


def convert_record_to_measurement(record: ForaMedicalRecord) -> List[BaseMeasurement]:
    res: List[BaseMeasurement] = []
    for measurement, value in record.get_measurement_with_values():
        res.extend(_build_measurement(measurement, value, record))
    return res
