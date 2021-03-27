from django.db import models
from django.conf import settings


class Exercise(models.Model):
    """
    Object for exercise instance to be used in exercise set
    """
    name = models.CharField(null=False, blank=False, max_length=100)
    description = models.TextField(null=False, blank=True, max_length=1000)
    instructions = models.TextField(null=False, blank=True, max_length=1000)
    tips = models.TextField(null=False, blank=True, max_length=1000)
    primary_muscles = models.ManyToManyField('body.Muscle', related_name='primary_muscles')
    secondary_muscles = models.ManyToManyField('body.Muscle', related_name='secondary_muscles', blank=True)

    def __str__(self):
    	return f"{self.primary_muscles.all().first()} - {self.name}"


class ExerciseSet(models.Model):
    """
    Object for exercise set instance
    """
    exercise = models.ForeignKey('gym.Exercise', null=False, blank=False, on_delete=models.CASCADE)
    sets = models.ManyToManyField('gym.Set', related_name='sets')
    number_of_sets = models.IntegerField(null=False, blank=False, default=4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


    def __str__(self):
    	return f"{self.exercise.name} - {self.number_of_sets} sets"


class Set(models.Model):
    """
    Object for set instance to be used in exercise set
    """
    REPS_UNIT = (('RE', 'Reps'), ('MI', 'Minutes'), ('SE', 'Seconds'), ('KM', 'kilometers'), ('UF', 'Until Failure'),)
    WEIGHT_UNIT = (('KG', 'Kg.'), ('BW', 'Body Weight'), ('KH', 'Kms per hour'),)

    reps = models.PositiveIntegerField(null=False, blank=False, default=0)
    reps_unit = models.CharField(max_length=2, choices=REPS_UNIT, default='RE')
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    weight_unit = models.CharField(max_length=2, choices=WEIGHT_UNIT, default='RE')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
    	return f"{self.reps} {self.reps_unit} x {self.weight} {self.weight_unit}"
