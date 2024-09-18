import re

from enum import StrEnum, Enum

HEMATOCRIT_TO_HEMOGLOBIN = 0.340000003576279

class Period(StrEnum):
    BEFORE_MEAL = 'Before Meal'
    AFTER_MEAL = 'After Meal'
    GENERIC = 'GEN'
    EMPTY = ''


class MeasurementUnit(Enum):
    MG_DL = 'mg/dl', 'mg_dl'
    G_DL = 'g/dl', 'g_dl'
    MMOL_L = 'mmol/L', 'mmol'
    UMOL_L = 'umol/L', 'umol'
    PERCENTAGE = '%', 'perc'

    # Credit: https://stackoverflow.com/a/59916706/5230043
    def __new__(cls, value, internal_property):
        obj = object.__new__(cls)
        obj._value_ = value
        obj._internal_property = internal_property
        return obj

    @staticmethod
    def get_unit_from_csv_header(header_name):
        if re.compile(r'.*_mg_dl').match(header_name):
            return MeasurementUnit.MG_DL
        elif re.compile(r'.*_g_dl').match(header_name):
            return MeasurementUnit.G_DL
        elif re.compile(r'.*_mmol').match(header_name):
            return MeasurementUnit.MMOL_L
        elif re.compile(r'.*_umol').match(header_name):
            return MeasurementUnit.UMOL_L
        elif re.compile(r'.*_perc').match(header_name):
            return MeasurementUnit.PERCENTAGE
        else:
            raise IndexError(f'Unrecognized header name: {header_name}')

    def get_medical_record_unit(self):
        return self._internal_property
