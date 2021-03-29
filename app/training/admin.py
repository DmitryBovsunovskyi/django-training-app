from django.contrib import admin

from training import models


admin.site.register(models.Workout)
admin.site.register(models.Exercise)
admin.site.register(models.ExerciseSet)
admin.site.register(models.Set)
