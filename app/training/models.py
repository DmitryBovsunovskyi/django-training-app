from django.db import models
from django.db import models
from django.db import models
from django.conf import settings
import datetime

from training.constants import REPS_UNIT_CHOICES, WEIGHT_UNIT_CHOICES, REST_UNIT_CHOICES


class Workout(models.Model):
    """
    Object for workout/training instance
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    date = models.DateField(default=datetime.date.today())
    aim = models.CharField(max_length=100, blank=True)
    # exercises = models.ManyToManyField('training.Exercise', related_name='exercises')

    def __str__(self):
        """
        If there is no name return date
        """
        return f"{self.name}"


class Exercise(models.Model):
    """
    Object for exercise instance to be used in exercise set
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    primary_muscles = models.ManyToManyField('body.Muscle', related_name='primary_muscles')
    secondary_muscles = models.ManyToManyField('body.Muscle', related_name='secondary_muscles', blank=True)

    def __str__(self):
    	return f"{self.primary_muscles.all().first()} - {self.name}"


class ExerciseSet(models.Model):
    """
    Object for exercise set instance
    """
    workout = models.ForeignKey('training.Workout',on_delete=models.CASCADE, related_name='exerciseset')
    muscles = models.ManyToManyField('body.Muscle', related_name='muscles', blank=True)
    exercise = models.ForeignKey('training.Exercise', on_delete=models.CASCADE, related_name='exercise')
    notes = models.TextField(blank=True)


    def __str__(self):
    	return f"{self.exercise}"


class Set(models.Model):
    """
    Object for set instance to be used in exercise set
    """
    exercise = models.ForeignKey('training.ExerciseSet', on_delete=models.CASCADE, related_name='set')
    done = models.BooleanField(default=False)
    reps = models.PositiveIntegerField(default=0)
    reps_unit = models.CharField(max_length=20, choices=REPS_UNIT_CHOICES.choices(), default=REPS_UNIT_CHOICES.REPS)
    weight = models.DecimalField(max_digits=20, decimal_places=2)
    weight_unit = models.CharField(max_length=20, choices=WEIGHT_UNIT_CHOICES.choices(), default=WEIGHT_UNIT_CHOICES.KG)
    rest = models.PositiveIntegerField(default=0)
    rest_unit = models.CharField(max_length=20, choices=REST_UNIT_CHOICES.choices(), default=REST_UNIT_CHOICES.MIN)

    def __str__(self):
    	return f"{self.reps} {self.reps_unit} x {self.weight} {self.weight_unit}"