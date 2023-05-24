from django.db import models


class Game(models.Model):
    name = models.CharField(max_length=88, unique=True)

    class Platform(models.TextChoices):
        BGA = 'BGA', 'BGA'
        Yucata = 'Yucata', "Yucata"

    platform = models.CharField(
        max_length=6,
        choices=Platform.choices,
        default=Platform.BGA
    )

    def __str__(self):
        return str(self.name)


class GameOption(models.Model):
    name = models.CharField(max_length=88)
    game = models.ForeignKey(Game, null=True, blank=True, on_delete=models.CASCADE, related_name='options')
    value = models.BooleanField(
        null=True,
        default=None
    )

    def __str__(self):
        return str(self.name)


class GameOptionChoice(models.Model):
    name = models.CharField(max_length=139, blank=True, null=True)
    is_active = models.BooleanField(
        default=False
    )
    option = models.ForeignKey(
        GameOption,
        on_delete=models.CASCADE,
        related_name='choices'
    )

    def __str__(self):
        return str(self.name)
