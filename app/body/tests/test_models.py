from django.test import TestCase

from body.models import Muscle, MuscleGroup


class TestBodyModels(TestCase):
    """
    Test Body models
    """
    def test_muscle_group_str(self):
        """
        Test MuscleGroup model`s string representation
        """
        muscle_group = MuscleGroup.objects.create(
            name='testname',
        )
        self.assertEqual(str(muscle_group), muscle_group.name)

    def test_muscle_str(self):
        """
        Test Muscle model`s string representation
        """
        muscle = Muscle.objects.create(
            name='testname'
        )
        self.assertEqual(str(muscle), muscle.name)
