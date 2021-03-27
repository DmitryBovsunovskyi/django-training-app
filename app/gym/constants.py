"""
Choices of repetition units for gym.set model
"""
REPETITIONS = 'RE'
MINUTES = 'MI'
SECONDS = 'SE'
KILOMETERS = 'KM'

REPS_UNIT_CHOICES = [
    (REPETITIONS, 'Repetitions'),
    (MINUTES, 'Minutes'),
    (SECONDS, 'Seconds'),
    (KILOMETERS, 'Kilometers'),
]

"""
Choices of weight units for gym.set model
"""
KILOGRAMS = 'KG'
BODY_WEIGHT = 'BW'
KMS_PER_HOUR = 'KH'

WEIGHT_UNIT_CHOICES = [
    (KILOGRAMS, 'Kilograms'),
    (BODY_WEIGHT, 'Body weight'),
    (KMS_PER_HOUR, 'Kilometers per hour'),

]

"""
Choices of rest units for gym.set model
"""
SECONDS = "sec"
MINUTES = "min"
HOURS = "hr"

REST_UNIT_CHOICES = [
    (SECONDS, 'Seconds'),
    (MINUTES, 'Minutes'),
    (HOURS, 'Hours'),
]
