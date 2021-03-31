from rest_framework import serializers
from body.models import Muscle
from training.models import Workout, Exercise, ExerciseSet, Set



class ExerciseSerializer(serializers.ModelSerializer):
    """
    Serializer for Exerciese object
    """
    primary_muscles = serializers.SlugRelatedField(
        many=True,
        queryset=Muscle.objects.all(),
        slug_field='name'
    )
    secondary_muscles = serializers.SlugRelatedField(
        many=True,
        queryset=Muscle.objects.all(),
        slug_field='name'
    )

    class Meta:
        model = Exercise
        fields = ('id', 'name', 'description', 'primary_muscles', 'secondary_muscles')


class SetSerializer(serializers.ModelSerializer):
    """
    Serializer for Set object
    """


    class Meta:
        model = Set
        fields = (
            'id', 'exercise', 'done', 'reps',
            'reps_unit', 'weight', 'weight_unit',
            'rest', 'rest_unit'
        )


class ExerciseSetSerializer(serializers.ModelSerializer):
    """
    Serializer for ExerciseSet object
    """
    set = SetSerializer(many=True, read_only=True)
    muscles = serializers.SlugRelatedField(
        many=True,
        queryset=Muscle.objects.all(),
        slug_field='name'
    )

    class Meta:
        model = ExerciseSet
        fields = ('id', 'workout', 'exercise', 'muscles', 'notes', 'set')


class WorkoutSerializer(serializers.ModelSerializer):
    """
    Serializer for Workout object
    """
    exerciseset = ExerciseSetSerializer(many=True, read_only=True)

    date = serializers.DateField()
    class Meta:
        model = Workout
        fields = ('id', 'user_id', 'name', 'date', 'aim','exerciseset')
        read_only_fields =('id',)
