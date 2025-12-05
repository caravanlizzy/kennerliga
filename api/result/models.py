from django.db import models

from game.models import SelectedGame, TieBreaker
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
        on_delete=models.CASCADE,
        related_name='results'
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name='results'
    )
    points = models.IntegerField(blank=True, null=True)
    starting_position = models.IntegerField(blank=True, null=True)
    position = models.PositiveIntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    decisive_tie_breaker = models.ForeignKey(
        TieBreaker,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='decisive_results'
    )
    tie_breaker_value = models.CharField(max_length=255, null=True, blank=True)
    faction = models.ForeignKey('game.Faction', on_delete=models.SET_NULL, null=True, blank=True)
    tie_breaker_resolved = models.BooleanField(default=False)

    def __str__(self):
        return (
            f"{self.player_profile.profile_name} - "
            f"{self.selected_game} - {self.season} - {self.league}"
        )
