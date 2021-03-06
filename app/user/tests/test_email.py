from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch
from django.core import mail
from rest_framework.test import APIClient
from rest_framework import status


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class TestEmailApiTest(TestCase):
    """ Test sending email with token to user """
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user:register')
        self.email_verify_url = reverse('user:email-verify')
        self.login_url = reverse('user:login')
        self.update_user_url = reverse('user:update')
        self.email_reset_url = reverse('user:request-reset-email')
        self.password_reset_complete = reverse('user:password-reset-complete')

        self.user_correct_data = {
            'email': 'test@londonapdev.com',
            'password': 'testpass',
            'name': 'Test name'
        }

    def test_send_email_should_succeed(self):
        """
        Test our email backend sends email
        """
        with self.settings(
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
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
        # mocking send_email function
        with patch(
            "user.utils.Util.send_email"
        ) as mocked_send_email_function:

            response = self.client.post(self.register_url, self.user_correct_data)

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            mocked_send_email_function.assert_called_with({
                # fetching email body with the token (that was sent)
                # for assertion using call_args method of path function
                'email_body': mocked_send_email_function.call_args[0][0]['email_body'],
                'to_email': self.user_correct_data['email'],
                'email_subject': 'Verify your email',
                }
            )

    def test_create_user_with_invalid_credentials_email_failed(self):
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

            response = self.client.post(self.register_url, payload)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            # expect function not to be called
            mocked_send_email_function.assert_not_called()

    def test_verifying_email_with_valid_token_succeed(self):
        """
        Test verifying email with valid sent token
        """
        # mocking send_email function
        with patch(
            "user.utils.Util.send_email"
        ) as mocked_send_email_function:

            response1 = self.client.post(self.register_url, self.user_correct_data)
            # getting token using call_args
            response2 = self.client.get(
                                    self.email_verify_url + mocked_send_email_function.call_args[0][0]['email_body'][-214::]
                                    )

            self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

            self.assertEqual(response2.status_code, status.HTTP_200_OK)

            self.assertEqual(mocked_send_email_function.call_count, 1)

    def test_verifying_email_with_invalid_token_failed(self):
        """
        Test verifying email with invalid sent token should fail
        """
        # mocking send_email function
        with patch(
            "user.utils.Util.send_email"
        ) as mocked_send_email_function:

            response1 = self.client.post(self.register_url, self.user_correct_data)
            # getting token using call_args
            # and cutting 1 item of token to make it invalid
            response2 = self.client.get(
                                    self.email_verify_url + mocked_send_email_function.call_args[0][0]['email_body'][-214:-1]
                                    )

            self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

            self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
            # expect function not to be called
            self.assertEqual(mocked_send_email_function.call_count, 1)

    def test_email_for_password_reset_sent_successfully(self):
        """
        Test that email for resetting password was sent successfully
        """

        with patch(
            "user.utils.Util.send_email"
        ) as mocked_send_email_function:

            response1 = self.client.post(self.register_url, self.user_correct_data)
            # verifying user email
            email = response1.data['email']
            user = get_user_model().objects.get(email=email)
            user.is_verified = True
            user.save()

            response2 = self.client.post(
                                    self.email_reset_url,
                                    {'email': self.user_correct_data['email']}
                                    )

            self.assertEqual(response2.status_code, status.HTTP_200_OK)
            mocked_send_email_function.assert_called_with({
                # fetching email body with the token (that was sent) for assertion using call_args method of path function
                'email_body': mocked_send_email_function.call_args[0][0]['email_body'],
                'to_email': self.user_correct_data['email'],
                'email_subject': 'Reset your password',
                }
            )

    def test_email_for_password_reset_was_not_sent(self):
        """
        Test that email for password reset was not sent if email is invalid
        """
        with patch(
            "user.utils.Util.send_email"
        ) as mocked_send_email_function:

            # email is not verified
            response = self.client.post(
                                    self.email_reset_url,
                                    {'email': self.user_correct_data['email']}
                                    )

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            mocked_send_email_function.assert_not_called()

    def test_verifying_correct_sent_token_succeed(self):
        """
        Test that token and uidb64 sent to email are valid
        """
        with patch(
            "user.utils.Util.send_email"
        ) as mocked_send_email_function:

            response1 = self.client.post(self.register_url, self.user_correct_data)
            # verifying user email
            email = response1.data['email']
            user = get_user_model().objects.get(email=email)
            user.is_verified = True
            user.save()
            # sending email to reset password
            self.client.post(self.email_reset_url, {'email': self.user_correct_data['email']})
            # checking if uidb64 and token for reset are valid in the sent link
            # by fetching them using call_args
            response2 = self.client.get(
                                        reverse('user:password-reset-confirm',
                                            args=[mocked_send_email_function.call_args[0][0]['email_body'][-44:-41],
                                                  mocked_send_email_function.call_args[0][0]['email_body'][-40:-1]]
                                            )
                                     )

            self.assertEqual(response2.status_code, status.HTTP_200_OK)

    def test_verifying_incorrect_sent_token_fails(self):
        """
        Test verification with invalid token fails
        """
        with patch(
            "user.utils.Util.send_email"
        ) as mocked_send_email_function:

            response1 = self.client.post(self.register_url, self.user_correct_data)
            # verifying user email
            email = response1.data['email']
            user = get_user_model().objects.get(email=email)
            user.is_verified = True
            user.save()
            # sending email to reset password
            self.client.post(self.email_reset_url, {'email': self.user_correct_data['email']})
            # making token sent invalid by fetching
            # it using call_args and cutting few symbols

            response2 = self.client.get(
                                    reverse('user:password-reset-confirm',
                                        args=[mocked_send_email_function.call_args[0][0]['email_body'][-44:-41],
                                              mocked_send_email_function.call_args[0][0]['email_body'][-40:-3]]
                                        )
                                    )

            self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reseting_password_with_correct_token_succeed(self):
        """
        Test that user can reset password with correct token successfully
        """
        with patch(
            "user.utils.Util.send_email"
        ) as mocked_send_email_function:

            response1 = self.client.post(self.register_url, self.user_correct_data)
            # verifying user email
            email = response1.data['email']
            user = get_user_model().objects.get(email=email)
            user.is_verified = True
            user.save()
            # sending email to reset password
            self.client.post(self.email_reset_url, {'email': self.user_correct_data['email']})
            # checking if uidb64 and token for reset are valid in the sent link
            # by fetching them using call_args
            response2 = self.client.get(
                                    reverse('user:password-reset-confirm',
                                        args=[mocked_send_email_function.call_args[0][0]['email_body'][-44:-41],
                                              mocked_send_email_function.call_args[0][0]['email_body'][-40:-1]]
                                        )
                                    )
            payload = {
                    "password": "newpassword",
                    "token": mocked_send_email_function.call_args[0][0]['email_body'][-40:-1],
                    "uidb64": mocked_send_email_function.call_args[0][0]['email_body'][-44:-41]
            }
            # setting new password for user
            response3 = self.client.patch(self.password_reset_complete, payload)

            self.assertEqual(response3.status_code, status.HTTP_200_OK)

    def test_sending_verification_to_changed_email_succeed(self):
        """
        Test that when user changed emal verification link is sent successfully
        """
        with patch(
            "user.utils.Util.send_email"
        ) as mocked_send_email_function:

            response1 = self.client.post(self.register_url, self.user_correct_data)
            email = response1.data['email']
            user = get_user_model().objects.get(email=email)
            user.is_verified = True
            user.save()
            response2 = self.client.post(self.login_url, self.user_correct_data)
            self.client.force_authenticate(user=user)

            payload = {'email': 'newemail@gmail.com', 'name': 'new name', 'password': 'newpassword123'}
            response3 = self.client.patch(self.update_user_url, payload)

            mocked_send_email_function.assert_called_with({
                # fetching email body with the token (that was sent)
                # for assertion using call_args method of path function
                'email_body': mocked_send_email_function.call_args[0][0]['email_body'],
                'to_email': payload['email'],
                'email_subject': 'Verify your email',
                }
                )

    def test_email_wasnt_sent_if_user_dont_change(self):
        """
        Test that email for verification was not sent if user did not change email
        """
        with patch(
            "user.utils.Util.send_email"
        ) as mocked_send_email_function:

            response1 = self.client.post(self.register_url, self.user_correct_data)
            email = response1.data['email']
            user = get_user_model().objects.get(email=email)
            user.is_verified = True
            user.save()
            response2 = self.client.post(self.login_url, self.user_correct_data)
            self.client.force_authenticate(user=user)

            payload = {'name': 'new name', 'password': 'newpassword123'}
            response3 = self.client.patch(self.update_user_url, payload)

            # expect function to be called 1 time when user is registered
            mocked_send_email_function.assert_called_with({
                # fetching email body with the token (that was sent)
                # for assertion using call_args method of path function
                'email_body': mocked_send_email_function.call_args[0][0]['email_body'],
                'to_email': self.user_correct_data['email'],
                'email_subject': 'Verify your email',
                }
                )
