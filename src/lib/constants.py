from enum import Enum


class MeasurementUnit(Enum):
    MG_DL = 'mg/dl'
    G_DL = 'g/dl'
    MMOL_L = 'mmol/L'
    PERCENTAGE = '%'


class Period(Enum):
    BEFORE_MEAL = 'Before Meal'
    AFTER_MEAL = 'After Meal'
    GENERIC = 'GEN'
    EMPTY = None
