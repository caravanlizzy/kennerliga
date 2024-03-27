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
    is_activated = models.BooleanField(
        null=True,
        default=None
    )

    def __str__(self):
        return str(self.name)


class GameOptionChoice(models.Model):
    name = models.CharField(max_length=139, blank=True, null=True)
    is_selected = models.BooleanField(
        default=False
    )
    option = models.ForeignKey(
        GameOption,
        on_delete=models.CASCADE,
        related_name='choices'
    )

    def __str__(self):
        return str(self.name)
