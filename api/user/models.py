from django.contrib.auth.models import AbstractUser
from django.db import models

from league.models import League
from season.models import Season


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
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='profile')
    platforms = models.ManyToManyField(Platform, through='PlatformPlayer')

    def get_last_participation(self):
        return Season.objects.filter(participants=self).order_by('-year', '-month').first()

    def get_league_membership(self, season):
        try:
            # Get the league where this player is a member for the given season
            return season.get_leagues().get(members=self)
        except League.DoesNotExist:
            print('Profile did not participate in this season')
            return None  # If no league is found, return None or handle accordingly

    def get_previous_season_result(self):
        previous_season = Season.get_previous_season()
        last_particpation = self.get_last_participation()
        if previous_season != last_particpation:
            # has not participated previous season therefore no result
            return None
        previous_membership = self.get_league_membership(previous_season)
        previous_position = None
        return previous_membership, previous_position

    def __str__(self):
        return self.profile_name


class PlatformPlayer(models.Model):
    player_profile = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('player_profile', 'platform')

    def __str__(self):
        return f"{self.name} on {self.platform.name}"
