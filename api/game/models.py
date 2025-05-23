from django.db import models

from league.models import League
from user.models import PlayerProfile, Platform


class Game(models.Model):
    name = models.CharField(max_length=88)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'platform'], name='unique_game_per_platform')
        ]

    def __str__(self):
        return str(self.name)


class GameOption(models.Model):
    name = models.CharField(max_length=88)
    game = models.ForeignKey(Game, null=True, blank=True, on_delete=models.CASCADE, related_name='options')
    has_choices = models.BooleanField(default=False)
    only_if_option = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                       related_name='only_if_options')
    only_if_choice = models.ForeignKey('GameOptionChoice', on_delete=models.CASCADE, null=True, blank=True,
                                       related_name='only_if_options')
    only_if_value = models.BooleanField(
        null=True,
        default=None
    )

    def __str__(self):
        return str(self.name)


class GameOptionChoice(models.Model):
    name = models.CharField(max_length=139, blank=True, null=True)
    option = models.ForeignKey(
        GameOption,
        on_delete=models.CASCADE,
        related_name='choices'
    )

    def __str__(self):
        return f"{self.name or '(Unnamed)'} for {self.option.name}"


class SelectedGame(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='selected_games')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='game_selections')
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='game_selections')

    def __str__(self):
        return f"{self.player}'s selection for {self.game.name}"


class SelectedOption(models.Model):
    selected_game = models.ForeignKey(SelectedGame, on_delete=models.CASCADE, related_name='selected_options')
    game_option = models.ForeignKey(GameOption, on_delete=models.CASCADE, related_name='selections')
    choice = models.ForeignKey(GameOptionChoice, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='selections')
    value = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"Option: {self.game_option.name}, Choice: {self.choice.name if self.choice else 'No choice'}, Value: {self.value}"


class BanDecision(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='ban_decisions')
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='ban_decisions')
    game = models.ForeignKey(SelectedGame, null=True, blank=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('league', 'player')

    def __str__(self):
        return f"{self.player} {'banned ' + str(self.game) if self.game else 'skipped banning'} in {self.league}"


class StartingPointSystem(models.Model):
    code = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.code


class ResultConfig(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    is_asymmetric = models.BooleanField(default=False)
    has_starting_player_order = models.BooleanField(default=True)
    starting_points_system = models.ForeignKey(StartingPointSystem, on_delete=models.SET_NULL, null=True, default=1)
    has_points = models.BooleanField(default=True)

    def __str__(self):
        return f"ResultConfig for {self.game}"


class TieBreaker(models.Model):
    result_config = models.ForeignKey(ResultConfig, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return str(self.name)


class Faction(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.game.name})"
