from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):

    # password = None in case you need to create a user that is not active
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a new User
        """
        if not email:
            raise ValueError("Users must have email address!")
        # normalize_email func makes email lowercase in case user provides Uppercase
        user = self.model(email=self.normalize_email(email), **extra_fields)
        # password has to be encrypted so we need to use set_password function
        user.set_password(password)
        # saving user with options "using=self._db" means that
        # multiple databases can be used in case we use more than 1 database in our project
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a new super user
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that supports using email insted of username
    """

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    # to determine if user is active or not, in case we want to deactivate user if we need
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    # by default it is user name but we want to change it to email
    USERNAME_FIELD = "email"
