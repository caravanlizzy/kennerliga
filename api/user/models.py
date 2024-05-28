from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    first_name = None
    last_name = None
    username = models.CharField(
        max_length=44,
        unique=True,
        blank=False,
        null=False,
        help_text='Username is used to login'
    )
    bga_name = models.CharField(
        max_length=88,
        blank=True,
        null=True
    )

    email = models.EmailField(
        'Email address',
        max_length=40,
        unique=True,
        help_text='Email address is used to contact the player'
    )

    USERNAME_FIELD = 'username'

    # REQUIRED_FIELDS = ['username']

    def __str__(self):
        return str(self.username)
