from enum import Enum


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]


class REPS_UNIT_CHOICES(ChoiceEnum):
    """
    Choices of repetition units for gym.set model
    """
    REPS = 'Repetitions'
    MIN = 'Minutes'
    SEC = 'Seconds'
    KM = 'Kilometers'


class WEIGHT_UNIT_CHOICES(ChoiceEnum):
    """
    Choices of weight units for gym.set model
    """
    KG = 'Kilograms'
    BW = 'Body weight'
    KH = 'Kilometers per hour'


class REST_UNIT_CHOICES(ChoiceEnum):
    """
    Choices of rest units for gym.set model
    """
    SEC = "seconds"
    MIN = "Minutes"
    HR = "Hours"
