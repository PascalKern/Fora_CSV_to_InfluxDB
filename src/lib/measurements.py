import dataclasses
import math
from dataclasses import dataclass
from datetime import datetime
from typing import List

from lib.constants import MeasurementUnit, Period, HEMATOCRIT_TO_HEMOGLOBIN
from lib.process_csv import ForaMedicalRecord, ForaMedicalRecords


# TODO Have a Measurements (container) class as well! Like for the Records! The measurements class should/could
#  then contain a filter method (via callback) to get only certain records
# TODO Add filter parameter (callback) to filter the records to be converted ie. save heap space!
#  Maybe the iteration could also just be done by streams ie. lazy on access to the records via the
#  (future) holding class of the method!
def convert_records_to_measurements(records: ForaMedicalRecords) -> List['BaseMeasurement']:
    res: List[BaseMeasurement] = []
    for record in records:
        res.extend(convert_record_to_measurement(record))
    return res


def convert_record_to_measurement(record: ForaMedicalRecord) -> List['BaseMeasurement']:
    res: List[BaseMeasurement] = []
    for measurement, value in record.get_measurements_and_values():
        meas_unit = MeasurementUnit.get_unit_from_csv_header(measurement)
        meas_type = measurement.replace('_' + meas_unit.get_medical_record_unit(), '')
        res.extend(_build_measurement(meas_type, value, meas_unit, record))
    return res


def _build_measurement(meas_type: str, value: float, meas_unit: MeasurementUnit,
                       record: ForaMedicalRecord) -> List['BaseMeasurement']:
    date_time = record.get_date_time()
    period = record.get_period()

    match meas_type:
        case 'hematocrit':
            hematocrit = Hematocrit(date_time=date_time, unit=meas_unit, value=value, period=period)
            return [hematocrit, hematocrit.build_hemoglobin_measurement()]
        case 'blood_glucose':
            return [BloodGlucose(date_time=date_time, unit=meas_unit, value=value, period=period)]
        case 'ketone':
            return [Ketnone(date_time=date_time, unit=meas_unit, value=value, period=period)]
        case 'cholesterol':
            return [Cholesterol(date_time=date_time, unit=meas_unit, value=value, period=period)]
        case 'uric_acid':
            return [UricAcid(date_time=date_time, unit=meas_unit, value=value, period=period)]
        case 'triglycerides':
            return [Triglycerides(date_time=date_time, unit=meas_unit, value=value, period=period)]
        case 'lactate':
            return [Lactate(date_time=date_time, unit=meas_unit, value=value, period=period)]
        case 'note':
            return [Note(date_time=date_time, unit=meas_unit, value=value, period=period)]
        case _:
            raise ValueError(f'Unexpected measurement type: {meas_type}')


@dataclass(frozen=True)
class BaseMeasurement(object):
    date_time: datetime                                             # InfluxDB schema: "key" aka Timeseries-PrimaryKey
    unit: MeasurementUnit                                           # InfluxDB schema: Attribute
    value: float | str                                              # InfluxDB schema: Measurement
    period: Period = Period.EMPTY                                   # InfluxDB schema: Attribute
    measurement_name: str = dataclasses.field(init=False)           # InfluxDB schema: Name
    default_unit: MeasurementUnit = dataclasses.field(init=False)   # InfluxDB schema: synthetic [opt. Attribute]
    calculated: bool = dataclasses.field(init=False, default=False) # InfluxDB schema: synthetic Attribute

    def __str__(self):
        res = ''
        for k, v in self.__items():
            import os
            res += f'{k:<24} -> {v}{os.linesep}'
        return res.strip()

    def __items(self):
        for cls_field in dataclasses.fields(self):
            yield cls_field.name, getattr(self, cls_field.name)


@dataclass(frozen=True)
class BloodGlucose(BaseMeasurement):
    measurement_name = 'blood_glucose'
    default_unit = MeasurementUnit.MG_DL


@dataclass(frozen=True)
class Hemoglobin(BaseMeasurement):
    measurement_name = 'hemoglobin'
    default_unit = MeasurementUnit.G_DL
    calculated = True


@dataclass(frozen=True)
class Hematocrit(BaseMeasurement):
    measurement_name = 'hematocrit'
    default_unit = MeasurementUnit.PERCENTAGE

    def build_hemoglobin_measurement(self, unit: MeasurementUnit = MeasurementUnit.MG_DL) -> Hemoglobin:
        return Hemoglobin(date_time=self.date_time, unit=unit, value=self._calc_hemoglobin(unit), period=self.period)

    # TODO Check if calculation still is correct and the unit handling too! Using the unit from build_hemaglobine_measurement ok?!
    def _calc_hemoglobin(self, unit: MeasurementUnit) -> float:
        if unit == MeasurementUnit.MG_DL:
            # Calculation from Android App code: FLOOR('Hematocrit(%)' × 0.340000003576279 × 10,1) ÷ 10
            return math.floor(self.value * HEMATOCRIT_TO_HEMOGLOBIN * 10) / 10
        elif unit == MeasurementUnit.MMOL_L:
            raise BaseException('Conversation from Hematocrit to Hemoglobin in mmol/l not yet implemented!')


@dataclass(frozen=True)
class Ketnone(BaseMeasurement):
    measurement_name = 'ketone'
    default_unit = MeasurementUnit.MMOL_L


@dataclass(frozen=True)
class Cholesterol(BaseMeasurement):
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


@dataclass(frozen=True)
class Note(BaseMeasurement):
    measurement_name = 'note'
    default_unit = MeasurementUnit.STRING

