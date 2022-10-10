from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser):
    nickname = models.CharField(
        max_length=44,
        blank=False,
        null=False,
    )
    email = models.EmailField(max_length=30)

