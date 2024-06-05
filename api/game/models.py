from django.db import models

from user.models import User

from league.models import League



class Platform(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.name)


class Game(models.Model):
    name = models.CharField(max_length=88)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    unique_together = ('name', 'platform')

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
        return str(self.name)


class SelectedGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='selected_games')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='selected_games')
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='selected_games')

    def __str__(self):
        return f"{self.user.username}'s selection for {self.game.name}"


class SelectedOption(models.Model):
    selected_game = models.ForeignKey(SelectedGame, on_delete=models.CASCADE, related_name='selected_options')
    game_option = models.ForeignKey(GameOption, on_delete=models.CASCADE, related_name='selections')
    choice = models.ForeignKey(GameOptionChoice, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='selections')
    value = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"Option: {self.game_option.name}, Choice: {self.choice.name if self.choice else 'No choice'}, Value: {self.value}"


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
        return str(self.name)
