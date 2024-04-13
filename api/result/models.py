from django.db import models
from user.models import User
from season.models import Season
from game.models import Game


# Create your models here.
class Result(models.Model):
    player = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    position = models.IntegerField()
    points = models.IntegerField()
    league = models.IntegerField()
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    year = models.IntegerField()
    starting_position = models.IntegerField(blank=True, null=True)
    starting_points = models.IntegerField(blank=True, null=True)
    league_points = models.IntegerField()
    percentage_of_winner = models.FloatField(blank=True, null=True)
    character = models.CharField(
        max_length=144,
       blank=True,
        null=True
    )
    tie_breaker = models.CharField(
        max_length=144,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.player.username + '_' + str(self.year) + '_' + 'S' + str(self.season) + '_' + 'L' + str(self.league)


class ResultShape(models.Model):
    game=models.ForeignKey(Game, on_delete=models.CASCADE)
    class StartingPointSystems(models.TextChoices):
        FIX = 'FIX', 'All players start with a specific amount of points. The amount is set per game'
        STARTING_POSITION = 'SP', 'Starting points depend on starting position'
        NONE = 'NONE', 'Game does not have any points'
        DYNAMIC = 'DYNAMIC', 'Starting points vary in each game'
    is_assymmetric = models.BooleanField(default=False)
    starting_position = models.BooleanField(default=True)
    starting_points = models.CharField(
        max_length=7,
        choices=StartingPointSystems.choices,
        default=StartingPointSystems.FIX
    )
    scoring_points=models.BooleanField(default=True)

class TieBreaker(models.Model):
    result_shape = models.ForeignKey(ResultShape, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

class Faction(models.Model):
    game=models.ForeignKey(Game, on_delete=models.CASCADE)
    result_shape=models.ForeignKey(ResultShape, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
