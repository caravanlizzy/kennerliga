from django.utils import timezone

from django.db import models

from game.models import SelectedGame
from season.models import Season
from user.models import PlayerProfile


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
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_finished(self) -> bool:
        from league.queries import is_league_finished
        return is_league_finished(self)

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


class LeagueStanding(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="standings")
    player_profile = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    wins = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # per your win_mode
    league_points = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 6/3/1/0 with tie-sharing
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("league", "player_profile")
        indexes = [
            models.Index(fields=["league", "-league_points", "-wins"]),
        ]

    def __str__(self):
        return f"{self.league} - {self.player_profile}: {self.league_points}"


class GameStanding(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="game_standings")
    selected_game = models.ForeignKey(SelectedGame, on_delete=models.CASCADE, related_name="standings")
    player_profile = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)

    # Per-game snapshot
    points = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rank = models.PositiveIntegerField()  # dense rank within the game
    league_points = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # tie-shared per rules
    win_share = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 1, fractional, or 0
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("selected_game", "player_profile")
        indexes = [
            models.Index(fields=["league", "selected_game"]),
            models.Index(fields=["league", "-league_points", "-points"], name="league_game_league__9b635e_idx"),
        ]

    def __str__(self):
        return f"{self.selected_game_id} - {self.player_profile}: {self.league_points}"
