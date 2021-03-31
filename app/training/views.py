from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, permissions, generics, viewsets, mixins
from rest_framework.views import APIView
from django.utils import timezone

from training.models import Workout, Exercise, ExerciseSet, Set
from training import serializers


class WorkoutView(viewsets.ModelViewSet):
    """
    Manage workout in database
    """
    queryset = Workout.objects.all()
    serializer_class = serializers.WorkoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Create a new object
        """
        serializer.save(user=self.request.user)

class ExerciseView(viewsets.ModelViewSet):
    """
    Manage exercise in database
    """
    queryset = Exercise.objects.all()
    serializer_class = serializers.ExerciseSerializer
    permission_classes = [permissions.IsAdminUser]

class ExerciseSetView(viewsets.ModelViewSet):
    """
    Manage exerciseset in database
    """
    queryset = ExerciseSet.objects.all()
    serializer_class = serializers.ExerciseSetSerializer
    permission_classes = [permissions.IsAuthenticated]

class SetView(viewsets.ModelViewSet):
    """
    Manage exerciseset in database
    """
    queryset = Set.objects.all()
    serializer_class = serializers.SetSerializer
    permission_classes = [permissions.IsAuthenticated]
