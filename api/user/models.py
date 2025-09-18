from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


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
    password = models.CharField(max_length=128, blank=False, null=False)
    USERNAME_FIELD = 'username'

    # REQUIRED_FIELDS = ['username']

    def __str__(self):
        return str(self.username)


class Platform(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.name)


class UserInvitation(models.Model):
    username = models.TextField()
    otp = models.TextField()
    failed_attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} invited at {self.created_at}"

    class Meta:
        ordering = ['-created_at']


class PlayerProfile(models.Model):
    profile_name = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='profile')
    platforms = models.ManyToManyField(Platform, through='PlatformPlayer')

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


class YearlyGameSelection(models.Model):
    player_profile = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='yearly_selections')
    year = models.IntegerField()
    game = models.ForeignKey('game.Game', on_delete=models.CASCADE)
    selection_count = models.IntegerField()  # Tracks how many times this game has been selected (1-3)
    selected_in_season = models.ForeignKey('season.Season', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-year', 'selected_in_season']
        constraints = [
            models.UniqueConstraint(
                fields=['player_profile', 'year', 'game', 'selection_count'],
                name='uniq_profile_year_game_selcount',
            ),
            models.CheckConstraint(
                check=Q(selection_count__in=[1, 2, 3]),
                name='valid_selection_count',
            ),
        ]

    def __str__(self):
        return f"{self.player_profile.profile_name}'s selection #{self.selection_count} of {self.game} in {self.year}"
