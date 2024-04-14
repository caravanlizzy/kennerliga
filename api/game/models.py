from django.db import models


class Game(models.Model):
    name = models.CharField(max_length=88)

    class Platform(models.TextChoices):
        BGA = 'BGA', 'BGA'
        Yucata = 'Yucata', "Yucata"

    platform = models.CharField(
        max_length=6,
        choices=Platform.choices,
        default=Platform.BGA
    )

    unique_together = ('name', 'platform')

    def __str__(self):
        return str(self.name)


class GameOption(models.Model):
    name = models.CharField(max_length=88)
    game = models.ForeignKey(Game, null=True, blank=True, on_delete=models.CASCADE, related_name='options')
    has_choices = models.BooleanField(default=False)
    only_if_option = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='only_if_options')
    only_if_choice = models.ForeignKey('GameOptionChoice', on_delete=models.CASCADE, null=True, blank=True, related_name='only_if_options')
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
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    option = models.ForeignKey(GameOption, on_delete=models.CASCADE)
    boolean_value = models.BooleanField(null=True, blank=True)
    choice_value = models.ForeignKey(GameOptionChoice, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.game.name} - {self.option.name}"

    @classmethod
    def create_selected_game(cls, game, option, boolean_value=None, choice_value=None):
        selected_game = cls(game=game, option=option)
        if option.has_choices:
            selected_game.choice_value = choice_value
        else:
            selected_game.boolean_value = boolean_value
        selected_game.save()
        return selected_game



class ResultConfig(models.Model):
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
    result_shape = models.ForeignKey(ResultConfig, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']


class Faction(models.Model):
    game=models.ForeignKey(Game, on_delete=models.CASCADE)
    result_shape=models.ForeignKey(ResultConfig, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
