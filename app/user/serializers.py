from django.contrib.auth import get_user_model, authenticate
# if you want to extend your code in the fututre, to support multiple languages
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import reverse
from .utils import Util


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the users object
    """
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """
        Create a new user with encrypted password and return it
        """
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """
        Update a user with encrypted password and return it
        """
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user


class EmailVerificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the token of user object
    """
    token = serializers.CharField(max_length=555)

    class Meta:
        model = get_user_model()
        fields = ['token']


class LoginSerializer(serializers.ModelSerializer):
    """
    Serializer for the user authentication object
    """
    email = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    name = serializers.CharField(max_length=50, min_length=5, read_only=True)
    tokens = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name', 'tokens']

    def validate(self, attrs):
        """ Validate and authenticate the user """
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg3 = _('Unable to authenticate with provided credentials')
            raise AuthenticationFailed(msg3)
        if not user.is_active:
            msg1 = _('Account is disabled, contact admin.')
            raise AuthenticationFailed(msg1)
        if not user.is_verified:
            msg2 = _('Email is not verified.')
            raise AuthenticationFailed(msg2)

        return {
            'email': user.email,
            'name': user.name,
            'tokens': user.tokens()
        }


class ResetPasswordEmailSerializer(serializers.Serializer):
    """
    Serializer for sending token for rest password for user
    """
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ["email"]

    def validate(self, attrs):

        email = attrs.get('email')
        if get_user_model().objects.filter(email=email).exists():
            return {'email': email }
        else:
            raise AuthenticationFailed('Provided email is invalid.', 401)



class SetNewPasswordSerializer(serializers.Serializer):
    """
    Serializer for resertting password for user
    """
    password = serializers.CharField(min_length=5, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)
