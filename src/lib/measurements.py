import dataclasses
from dataclasses import dataclass
from datetime import datetime
from typing import List

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


def _build_measurement(measurement: str, value: float, date_time: datetime, period: Period,
                       note: str = '') -> BaseMeasurement:
    match measurement:
        case 'blood_glucose_mg_dl':
            return BloodGlucose(date_time=date_time, note=note, unit=MeasurementUnit.MG_DL, value=value, period=period)
        case 'blood_glucose_mmol':
            return BloodGlucose(date_time=date_time, note=note, unit=MeasurementUnit.MMOL_L, value=value, period=period)
        case 'hematocrit':
            return Hematocrit(date_time=date_time, note=note, unit=MeasurementUnit.PERCENTAGE, value=value, period=period)
        case 'ketone_mmol':
            pass
        case 'ketone_mg_dl':
            pass
        case 'hemoglobin_mmol':
            return Hemoglobin(date_time=date_time, note=note, unit=MeasurementUnit.MMOL_L, value=value, period=period)
        case 'hemoglobin_g_dl':
            return Hemoglobin(date_time=date_time, note=note, unit=MeasurementUnit.G_DL, value=value, period=period)
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


def convert_record_to_measurement(record: ForaMedicalRecord) -> List[BaseMeasurement]:
    res = []
    date_time = record.get_date_time()
    period = record.get_period()
    note = record.get_note()
    for measurement, value in record.get_measurement_with_values():
        res.append(_build_measurement(measurement, value, date_time, period, note))
    return res
