from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):

    """
    Mandatory Fields:
        - email
    Additional Fields:
        - first_name
        - last_name
        - telegram_alias
        - status

    Statuses types:
        1 - common user
        2 - admin
    """

    email = models.EmailField(unique=True, primary_key=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    telegram_alias = models.CharField(max_length=100, blank=True)
    status = models.IntegerField(default=1, validators=[MinValueValidator(1),
                                                        MaxValueValidator(2)])

    def __str__(self):
        return f'{self.email} Profile'
