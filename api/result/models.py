from django.db import models
from user.models import User
from season.models import Season
from league.models import League
from game.models import SelectedGame

class Result(models.Model):
    user=models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    selected_game=models.ForeignKey(
            SelectedGame,
            on_delete=models.CASCADE,
    )
    league=models.ForeignKey(
            League,
            on_delete=models.CASCADE
    )
    season=models.ForeignKey(
            Season,
            on_delete=models.CASCADE
    )
    points=models.IntegerField(blank=True, null=True)
    startin_position=models.IntegerField(blank=True, null=True)
    decisive_tie_breaker=models.CharField(max_length=255, null=True, blank=True)
    tie_breaker_value=models.CharField(max_length=255, null=True, blank=True)

    def __string__(self):
        return self.user.username + str(self.selected_game) + str(self.season) + str(self.league)

