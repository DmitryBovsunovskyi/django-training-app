from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class TestUserApi(TestCase):
    """
    Test the users API (public)
    """

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user:register')
        self.login_url = reverse('user:login')

        self.user_correct_data = {
            'email': 'test@londonapdev.com',
            'password': 'testpass',
            'name': 'Test name'
        }

    def test_create_valid_user_success(self):
        """
        Test creating user with valid payload is successful
        """
        res = self.client.post(self.register_url, self.user_correct_data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(self.user_correct_data['password']))
        self.assertNotIn('password', res.data)
        self.assertEqual(self.user_correct_data['email'], res.data['email'])
        self.assertEqual(self.user_correct_data['name'], res.data['name'])

    def test_user_exists(self):
        """
        Test creating user that already exists fails
        """
        create_user(**self.user_correct_data)

        res = self.client.post(self.register_url, self.user_correct_data)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """
        Test that password must be more than 5 characters
        """
        payload = {
            'email': 'test@londonapdev.com',
            'password': 'pw',
            'name': 'Test name'
        }
        res = self.client.post(self.register_url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_invalid_email(self):
        """
        Test that email provided is Invalid
        """
        payload = {
            'email': 'testlondonapdev.com',
            'password': 'pw',
            'name': 'Test name'
        }
        res = self.client.post(self.register_url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_register_with_no_data(self):
        """
        Test that user can not register with no data Provided
        """
        res = self.client.post(self.register_url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_login_with_unverifie_email(self):
        """
        Test that user cannot login with unverified email
        """
        self.client.post(self.register_url, self.user_correct_data)
        res = self.client.post(self.login_url, self.user_correct_data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_login_after_email_verification(self):
        """
        Test that user can login after his email was verified
        """
        response1 = self.client.post(self.register_url, self.user_correct_data)
        email = response1.data['email']
        user = get_user_model().objects.get(email=email)
        user.is_verified = True
        user.save()
        response2 = self.client.post(self.login_url, self.user_correct_data)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
