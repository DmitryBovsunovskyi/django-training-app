from django.urls import path, include
from rest_framework.routers import DefaultRouter

from training import views


router = DefaultRouter()
router.register('workouts', views.WorkoutView)
router.register('exercises', views.ExerciseView)
router.register('exercisesets', views.ExerciseSetView)
router.register('sets', views.SetView)

app_name = 'training'

urlpatterns = [
    path('', include(router.urls)),
]
