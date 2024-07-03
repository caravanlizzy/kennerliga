from django.db import models

from season.models import Season
from user.models import PlayerProfile


# Create your models here.
class League(models.Model):
    class LeagueStatus(models.TextChoices):
        PICKING = 'Spielwahl'
        BANNING = 'Bannen'
        PLAYING = 'Spielen'

    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    level = models.IntegerField('1 for L1, 2 for L2 etc.')
    members = models.ManyToManyField(PlayerProfile, related_name='leagues_member')

    def __str__(self):
        return f'{self.season}L{self.number}'
