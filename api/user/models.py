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


class Platform(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.name)


class PlayerProfile(models.Model):
    profile_name = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='player')
    platforms = models.ManyToManyField(Platform, through='PlatformPlayer')

    def __str__(self):
        return self.profile_name


class PlatformPlayer(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('player', 'platform')

    def __str__(self):
        return f"{self.name} on {self.platform.name}"
