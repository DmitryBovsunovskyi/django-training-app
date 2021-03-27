from django.db import models
from django.conf import settings

from gym.constants import REPS_UNIT_CHOICES, WEIGHT_UNIT_CHOICES, REST_UNIT_CHOICES


class Exercise(models.Model):
    """
    Object for exercise instance to be used in exercise set
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, max_length=1000)
    instructions = models.TextField(blank=True, max_length=1000)
    tips = models.TextField(blank=True, max_length=1000)
    primary_muscles = models.ManyToManyField('body.Muscle', related_name='primary_muscles')
    secondary_muscles = models.ManyToManyField('body.Muscle', related_name='secondary_muscles', blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
    	return f"{self.primary_muscles.all().first()} - {self.name}"


class ExerciseSet(models.Model):
    """
    Object for exercise set instance
    """
    exercise = models.ForeignKey('gym.Exercise', on_delete=models.CASCADE)
    number_of_sets = models.IntegerField(default=4)
    sets = models.ManyToManyField('gym.Set', related_name='sets')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


    def __str__(self):
    	return f"{self.exercise.name} - {self.number_of_sets} sets"


class Set(models.Model):
    """
    Object for set instance to be used in exercise set
    """
    reps = models.PositiveIntegerField(default=0)
    reps_unit = models.CharField(max_length=20, choices=REPS_UNIT_CHOICES, default='REPETITIONS')
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    weight_unit = models.CharField(max_length=20, choices=WEIGHT_UNIT_CHOICES, default='KILOGRAMS')
    rest = models.PositiveIntegerField(default=0)
    rest_unit = models.CharField(max_length=15, choices=REST_UNIT_CHOICES, default='Seconds')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
    	return f"{self.reps} {self.reps_unit} x {self.weight} {self.weight_unit}"
