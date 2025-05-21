from django.db import models

from season.models import Season


class LeagueStatus(models.TextChoices):
    PICKING = 'PICKING'
    BANNING = 'BANNING'
    REPICKING = 'REPICKING'
    PLAYING = 'PLAYING'
    DONE = 'DONE'


# Create your models here.
class League(models.Model):
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='leagues',
    )
    level = models.IntegerField('1 for L1, 2 for L2 etc.')
    members = models.ManyToManyField('season.SeasonParticipant', related_name='leagues_member')
    active_player = models.ForeignKey('season.SeasonParticipant', on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=LeagueStatus.choices,
        default=LeagueStatus.PICKING
    )

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
