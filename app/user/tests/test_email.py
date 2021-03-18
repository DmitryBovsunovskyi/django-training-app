from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch
from django.core import mail
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status


CREATE_USER_URL = reverse('user:register')
EMAIL_VERIFY_URL = reverse('user:email-verify')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class TestEmailApiTest(TestCase):
    """ Test sending email with token to user """
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()

    def test_send_email_should_succeed(self):
        """
        Test our email backend sends email
        """
        with self.settings(
            EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
        ):
            self.assertEqual(len(mail.outbox), 0)

            mail.send_mail(
                subject="Test subject",
                message="Test message",
                from_email="testmail@gmail.com",
                recipient_list=["testmail1994@gmail.com"],
                fail_silently=False,
            )

            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, "Test subject")

    def test_create_valid_user_successfully_sends_email(self):
        """
        Test creating user with valid payload should send email with token
        """
        payload = {
            'email': 'test@testemail.com',
            'password': 'testpass',
            'name': 'Test name'
        }

        # mocking send_email function
        with patch(
            "user.utils.Util.send_email"
        ) as mocked_send_email_function:

            response = self.client.post(CREATE_USER_URL, payload)

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            mocked_send_email_function.assert_called_with({
                # to omit creating second token as it will be created and sent while registrating in "response"
                # we can fetch a token for assertion using call_args method of path function
                'email_body': mocked_send_email_function.call_args[0][0]['email_body'],
                'to_email': payload['email'],
                'email_subject': 'Verify your email',
                }

            )

    def test_create_user_with_invalid_credentials_failed(self):
        """
        Test creating user with invalid credentials will fail and won`t send email
        """
        payload = {
            'email': 'invalidemail',
            # min lenth is 6
            'password': 'one',
            # can`t be empty
            'name': ''
        }

        # mocking send_email function
        with patch(
            "user.utils.Util.send_email"
        ) as mocked_send_email_function:

            response = self.client.post(CREATE_USER_URL, payload)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            # expect function not to be called
            mocked_send_email_function.assert_not_called()

    def test_verifying_email_with_valid_token_succeed(self):
        """
        Test verifying email with valid sent token
        """
        payload = {
            'email': 'test@testemail.com',
            'password': 'testpass',
            'name': 'Test name'
        }
        # mocking send_email function
        with patch(
            "user.utils.Util.send_email"
        ) as mocked_send_email_function:

            response1 = self.client.post(CREATE_USER_URL, payload)
            # getting the full request path using call_args
            response2 = self.client.get(mocked_send_email_function.call_args[0][0]['email_body'][-254::])

            self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

            self.assertEqual(response2.status_code, status.HTTP_200_OK)
            # expect function not to be called
            self.assertEqual(mocked_send_email_function.call_count, 1)

    def test_verifying_email_with_invalid_token_failed(self):
        """
        Test verifying email with invalid sent token should fail
        """
        payload = {
            'email': 'test@testemail.com',
            'password': 'testpass',
            'name': 'Test name'
        }
        # mocking send_email function
        with patch(
            "user.utils.Util.send_email"
        ) as mocked_send_email_function:

            response1 = self.client.post(CREATE_USER_URL, payload)
            # getting full request path using call_args and cutting 1 item of token to make it invalid
            response2 = self.client.get(mocked_send_email_function.call_args[0][0]['email_body'][-254:-1])

            self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

            self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
            # expect function not to be called
            self.assertEqual(mocked_send_email_function.call_count, 1)
