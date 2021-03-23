from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.test import force_authenticate


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
        self.update_user_url = reverse('user:update')
        self.logout_user_url = reverse('user:logout')
        self.users_list = reverse('user:user-list')

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

    def test_user_change_password_name_succeed(self):
        """
        Test that user can change password, name successfully
        """
        response1 = self.client.post(self.register_url, self.user_correct_data)
        email = response1.data['email']
        user = get_user_model().objects.get(email=email)
        user.is_verified = True
        user.save()
        response2 = self.client.post(self.login_url, self.user_correct_data)
        self.client.force_authenticate(user=user)
        payload = {'name': 'new name', 'password': 'newpassword123'}
        response3 = self.client.patch(self.update_user_url, payload)

        user.refresh_from_db()
        self.assertEqual(user.name, payload['name'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertEqual(response3.status_code, status.HTTP_200_OK)

    def test_user_updated_email_is_normalized(self):
        """
        Test when user updates email it is normalized
        """
        response1 = self.client.post(self.register_url, self.user_correct_data)
        email = response1.data['email']
        user = get_user_model().objects.get(email=email)
        user.is_verified = True
        user.save()
        response2 = self.client.post(self.login_url, self.user_correct_data)
        self.client.force_authenticate(user=user)
        payload = {'name': 'new name', 'email': 'Newemail@GMaiL.cOm', 'password': 'newpassword123'}
        response3 = self.client.patch(self.update_user_url, payload)

        user.refresh_from_db()
        self.assertEqual(user.name, payload['name'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertEqual(user.email, 'Newemail@gmail.com')
        self.assertEqual(response3.status_code, status.HTTP_200_OK)

    def test_user_is_not_verified_after_email_change(self):
        """
        Test that user is not verified after changing email
        """
        response1 = self.client.post(self.register_url, self.user_correct_data)
        email = response1.data['email']
        user = get_user_model().objects.get(email=email)
        user.is_verified = True
        user.save()
        response2 = self.client.post(self.login_url, self.user_correct_data)
        self.client.force_authenticate(user=user)
        payload = {'name': 'new name', 'email': 'Newemail@GMaiL.cOm', 'password': 'newpassword123'}
        response3 = self.client.patch(self.update_user_url, payload)

        user.refresh_from_db()
        self.assertFalse(user.is_verified)


    def test_retrive_profile_success(self):
        """
        Test retriving profile for logged in user
        """
        response1 = self.client.post(self.register_url, self.user_correct_data)
        email = response1.data['email']
        user = get_user_model().objects.get(email=email)
        user.is_verified = True
        user.save()
        response2 = self.client.post(self.login_url, self.user_correct_data)
        self.client.force_authenticate(user=user)
        response3 = self.client.get(self.update_user_url)

        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        self.assertEqual(response3.data, {
            'name': user.name,
            'email': user.email
        })

    def test_that_user_cant_see_users_list(self):
        """
        Test that common user has no permission to see list of users
        """
        response1 = self.client.post(self.register_url, self.user_correct_data)
        email = response1.data['email']
        user = get_user_model().objects.get(email=email)
        user.is_verified = True
        user.save()
        response2 = self.client.post(self.login_url, self.user_correct_data)
        self.client.force_authenticate(user=user)
        response3 = self.client.get(self.users_list)

        self.assertEqual(response3.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_logout_successfully(self):
        """
        Test that user can logout successfully
        """
        response1 = self.client.post(self.register_url, self.user_correct_data)
        email = response1.data['email']
        user = get_user_model().objects.get(email=email)
        user.is_verified = True
        user.save()
        response2 = self.client.post(self.login_url, self.user_correct_data)
        self.client.force_authenticate(user=user)
        response3 = self.client.post(self.logout_user_url, {'refresh': response2.data['tokens']['refresh']})

        self.assertEqual(response3.status_code, status.HTTP_204_NO_CONTENT)
