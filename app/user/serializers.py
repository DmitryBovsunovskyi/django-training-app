from django.contrib.auth import get_user_model, authenticate
# if you want to extend your code in the fututre, to support multiple languages
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed

from rest_framework import serializers


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
