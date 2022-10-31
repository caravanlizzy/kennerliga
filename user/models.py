from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    first_name = None
    last_name = None
    username = models.CharField(
        max_length=44,
        blank=False,
        null=False,
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
        help_text='Email address is used to login and to contact the User'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return str(self.username)
