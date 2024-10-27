from django.db import models

from season.models import Season


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
        related_name='season',
    )
    level = models.IntegerField('1 for L1, 2 for L2 etc.')
    members = models.ManyToManyField('user.PlayerProfile', related_name='leagues_member')
    active_player = models.ForeignKey('user.PlayerProfile', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.season}L{self.level}'


class LeagueResult(models.Model):
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE
    )
    profile = models.ForeignKey(
        'user.PlayerProfile',
        on_delete=models.CASCADE,
        related_name='league_results'
    )
    league_points = models.FloatField()
    position = models.IntegerField()
    last = models.BooleanField()
