from django.db import models

from game.models import SelectedGame
from league.models import League
from season.models import Season
from user.models import PlayerProfile


class Result(models.Model):
    player_profile = models.ForeignKey(
        PlayerProfile,
        on_delete=models.CASCADE,
    )
    selected_game = models.ForeignKey(
        SelectedGame,
        on_delete=models.CASCADE,
    )
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE
    )
    points = models.IntegerField(blank=True, null=True)
    startin_position = models.IntegerField(blank=True, null=True)
    decisive_tie_breaker = models.CharField(max_length=255, null=True, blank=True)
    tie_breaker_value = models.CharField(max_length=255, null=True, blank=True)

    def __string__(self):
        return self.player_profile.profile_name + str(self.selected_game) + str(self.season) + str(self.league)
