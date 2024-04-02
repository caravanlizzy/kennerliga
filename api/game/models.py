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
