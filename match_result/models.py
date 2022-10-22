from django.db import models
from user.models import User
from season.models import Season


# Create your models here.
class MatchResult(models.Model):
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

    def __str__(self):
        return self.player.username + '_' + str(self.year) + '_' + 'S' +  str(self.season) + '_' + 'L' + str(self.league)
