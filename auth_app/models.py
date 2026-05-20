from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


class CustomUserManager(UserManager):
    """User manager that automatically uses the email address as 'username'."""

    def create_user(self, email, password=None, **extra_fields):
        """Creates a regular user and automatically uses the email as 'username'."""
        # Django's default UserManager requires a 'username' field; we mirror the email there.
        return super().create_user(
            username=email,
            email=email,
            password=password,
            **extra_fields
        )

    def create_superuser(self, email, password=None, **extra_fields):
        """Creates a superuser and automatically uses the email as 'username'."""
        return super().create_superuser(
            username=email,
            email=email,
            password=password,
            **extra_fields
        )


class User(AbstractUser):
    """Custom user model that uses email as the login field and includes a 'fullname' field."""

    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=255)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname']

    objects = CustomUserManager()

    def __str__(self):
        """Returns the email address as the string representation of the user."""
        return self.email
