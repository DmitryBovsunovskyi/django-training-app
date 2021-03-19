from rest_framework import generics, status, authentication, permissions, views
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import serializers
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.encoding import (smart_str,
                                   force_str,
                                   smart_bytes,
                                   DjangoUnicodeDecodeError)

from user.serializers import (UserSerializer,
                              EmailVerificationSerializer,
                              LoginSerializer,
                              ResetPasswordEmailSerializer,
                              SetNewPasswordSerializer
                              )


class RegisterUserView(generics.GenericAPIView):
    """
    Register a new user in the system
    """
    serializer_class = UserSerializer

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data

        user = get_user_model().objects.get(email=user_data['email'])

        # will give us 2 tokens access and refresh tokens
        token = RefreshToken.for_user(user).access_token
        current_site = get_current_site(request).domain
        relative_link = reverse('user:email-verify')

        abs_url = 'http://' + current_site + relative_link + "?token=" + str(token)

        email_body = "Hello " + user.name + '!' + ' Use link below to verify your email \n' + abs_url

        data = {
            'email_body': email_body,
            'to_email': user.email,
            'email_subject': 'Verify your email'
        }
        Util.send_email(data)

        return Response(user_data, status=status.HTTP_201_CREATED)


class VerifyEmailView(views.APIView):
    """
    Verify a user by email with sent token
    """
    serializer_class = EmailVerificationSerializer
    token_param_config = openapi.Parameter(
        'token',
        in_=openapi.IN_QUERY,
        description="Description",
        type=openapi.TYPE_STRING
    )

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(
                jwt=token,
                key=settings.SECRET_KEY,
                algorithms=['HS256']
                )
            user = get_user_model().objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()

            return Response({'email': 'Successfully activated !'}, status=status.HTTP_200_OK)
        # in case token is expired
        except jwt.ExpiredSignatureError as indentifier:
            return Response({'error': 'Activation Expired !'}, status=status.HTTP_400_BAD_REQUEST)
        # in case token is invalid
        except jwt.exceptions.DecodeError as indentifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginUserView(generics.GenericAPIView):
    """
    Login user in to the system
    """
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordResetEmail(generics.GenericAPIView):
    """
    Password reset email for the user
    """
    serializer_class = ResetPasswordEmailSerializer

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:

            email = serializer.data.get('email')
            user = get_user_model().objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relative_link = reverse('user:password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

            abs_url = 'http://' + current_site + relative_link

            email_body = "Hello, \n Use the link below to reset your password \n" + abs_url

            data = {
                'email_body': email_body,
                'to_email': user.email,
                'email_subject': 'Reset your password'
            }
            Util.send_email(data)

            return Response({'success': 'The link to reset your password was sent to email.'}, status=status.HTTP_200_OK)

        except Exception as e:

            return Response({'error': 'Provided email is not valid!'}, status=status.HTTP_401_UNAUTHORIZED)



class PasswordTokenCheckApi(generics.GenericAPIView):
    """
    Checking token to reset email  for user
    """
    def get(self, request, uidb64, token):

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({'success': True, 'message': 'Credentials are valid', 'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError:
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)


class SetNewPasswordView(generics.GenericAPIView):
    """
    Setting new password for user
    """
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)

        return Response({'success': True, 'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
