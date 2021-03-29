from django.db import models


class MuscleGroup(models.Model):
    """
    Object for muscle group instance to be used in muscle
    """
    name = models.CharField(null=False, blank=False, max_length=100)
    description = models.TextField(null=False, blank=True, max_length=1000)
    benefits = models.TextField(null=False, blank=True, max_length=1000)
    basics = models.TextField(null=False, blank=True, max_length=1000)

    def __str__(self):
    	return f"{self.name}"


class Muscle(models.Model):
    """
    Object for muscle instance to be used in exercise
    """
    name = models.CharField(null=False, blank=False, max_length=100)
    description = models.TextField(null=False, blank=True, max_length=1000)
    basics = models.TextField(null=False, blank=True, max_length=1000)
    muscle_group = models.ForeignKey('body.MuscleGroup', null=True, on_delete=models.SET_NULL)

    def __str__(self):
    	return f"{self.name}"
