from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
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
        email = Util.normalize_email(validated_data.pop('email', None))
        validated_data['email'] = email
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
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):

        user = get_user_model().objects.get(email=obj['email'])
        return {
            'access': user.tokens()['access'],
            'refresh': user.tokens()['refresh']
        }

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name', 'tokens']

    def validate(self, attrs):
        """ Validate and authenticate the user """
        email = attrs.get('email', '')
        password = attrs.get('password', '')

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
        if not user.is_verified and not user.is_superuser:
            msg2 = _('Email is not verified.')
            raise AuthenticationFailed(msg2)

        return {
            'email': user.email,
            'name': user.name,
            'tokens': user.tokens
        }

        return super().validate(attrs)


class ResetPasswordEmailSerializer(serializers.Serializer):
    """
    Serializer for sending token for rest password for user
    """
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ["email"]

    def validate(self, attrs):

        email = attrs.get('email', '')
        if get_user_model().objects.filter(email=email).exists():
            return {'email': email}
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
            password = attrs.get('password', '')
            token = attrs.get('token', '')
            uidb64 = attrs.get('uidb64', '')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)


class LogOutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('bad_token')
