import dataclasses
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Type

from dataclass_csv import DataclassReader, dateformat, accept_whitespaces

from lib.constants import Period, MeasurementUnit
# Not nice but the only way to prevent the circular import at runtime! (https://stackoverflow.com/a/39757388/5230043)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.measurements import BaseMeasurement


@dataclass(frozen=True)
@dateformat('%Y/%m/%d %H:%M')  # 2024/07/24 14:48
@accept_whitespaces
class BaseForaMedicalRecord(object):
    _field_filter = ['_field_filter', 'date_time', 'period'] # Exclude this field and all properties set by the base class

    date_time: datetime
    period: Period = dataclasses.field(default=Period.EMPTY)
    note: str = dataclasses.field(default="")

    def _items(self):
        for cls_field in dataclasses.fields(self):
            yield cls_field.name, getattr(self, cls_field.name)

    def get_date_time(self) -> datetime:
        return self.date_time

    def get_period(self) -> Period:
        return self.period


@dataclass(frozen=True)
class ForaMedicalRecord(BaseForaMedicalRecord):
    blood_glucose_mg_dl: float = 0
    blood_glucose_mmol: float = 0
    hematocrit_perc: float = 0
    ketone_mmol: float = 0
    ketone_mg_dl: float = 0
    hemoglobin_mmol: float = 0
    hemoglobin_g_dl: float = 0
    cholesterol_mg_dl: float = 0
    cholesterol_mmol: float = 0
    uric_acid_mg: float = 0
    uric_acid_umol: float = 0
    uric_acid_mmol: float = 0
    triglycerides_mg_dl: float = 0
    triglycerides_mmol: float = 0
    lactate_mmol: float = 0

    def get_measurements_and_values(self, include_empty_values: bool = False) -> List[tuple[str, float]]:
        res = []
        for k, v in self.__class__._items(self):
            if k not in self._field_filter and (type(v) is str or v > 0 or include_empty_values):   # Exclude all properties set by the base class
                res.append((k, v))
        return res

    def get_note(self) -> str:
        return self.note

    def get_measurement(self, name: Type['BaseMeasurement'], unit: MeasurementUnit) -> float:
        return getattr(self, f'{name.measurement_name}_{unit.get_medical_record_unit()}')

    def __str__(self):
        res = ''
        for k, v in self._items():
            res += f'{k:<24} -> {v}{os.linesep}'
        return res.strip()


class ForaMedicalRecords(object):
    def __init__(self, reader: DataclassReader = None):
        self._reader = list(reader) if reader is not None else []

    def __iter__(self):
        yield from self._reader

    def get_record(self, rec_id: int) -> ForaMedicalRecord:
        return self._reader[rec_id]

    def __str__(self):
        return f'{os.linesep}{"Next Record":=^32}{os.linesep}'.join(map(str, self._reader))


# TODO Handle different 'measured value units' ie mg/dl or mmol/L
HEADER_MAPPING = {
    'Date/Time': 'date_time',
    'Period': 'period',
    'Note': 'note',
    'Blood Glucose(mg/dL)': 'blood_glucose_mg_dl',
    'Blood Glucose(mmol/L)': 'blood_glucose_mmol',
    'Hematocrit(%)': 'hematocrit_perc',
    'Ketone(mmol/L)': 'ketone_mmol',
    'Ketone(mg/dL)': 'ketone_mg_dl',
    'Hemoglobin((mmol/L))': 'hemoglobin_mmol',
    'Hemoglobin((g/dL))': 'hemoglobin_g_dl',
    'Cholesterol(mg/dL)': 'cholesterol_mg_dl',
    'Cholesterol(mmol/L)': 'cholesterol_mmol',
    'Uric Acid(mg/dL)': 'uric_acid_mg_dl',
    'Uric Acid(umol/L)': 'uric_acid_umol',
    'Uric Acid(mmol/L)': 'uric_acid_mmol',
    'Triglycerides(mg/dL)': 'triglycerides_mg_dl',
    'Triglycerides(mmol/L)': 'triglycerides_mmol',
    'Lactate(mmol/L)': 'lactate_mmol'
}

def read_csv(csv_file: Path) -> ForaMedicalRecords:
    """
    :param csv_file: csv file path
    :rtype: List[ForaMedicalRecord]
    """
    with csv_file.open() as csv_data:
        reader = DataclassReader(f=csv_data, cls=ForaMedicalRecord, )
        for k, v in HEADER_MAPPING.items():
            reader.map(k).to(v)
        return ForaMedicalRecords(reader)
