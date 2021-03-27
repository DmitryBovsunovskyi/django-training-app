from django.db import models

from workoutplan.constants import DAY_CHOICES


class WorkOutPlan(models.Model):
    """
    Workout plan object
    """
    day = models.CharField(choices=DAY_CHOICES, default='Monday', max_length=20)
    exercises = models.ManyToManyField('gym.ExerciseSet', related_name='exercises')
    aim = models.CharField(max_length=256, blank=True)

    def __str__(self):

     return f"{self.day} - {self.aim[0:7]}..."
