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

    USERNAME_FIELD = 'username'

    # REQUIRED_FIELDS = ['username']

    def __str__(self):
        return str(self.username)
