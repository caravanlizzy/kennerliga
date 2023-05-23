from django.db import models


# Create your models here.
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


class GameSettingsCategory(models.Model):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='categories'
    )
    name = models.CharField(max_length=88)
    value = models.BooleanField(
        blank=True,
        null=True,
        default=None
    )

    def __str__(self):
        return str(self.name)


class GameSettingsOptionChoice(models.Model):
    category = models.ForeignKey(
        GameSettingsCategory,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='options'
    )
    choice = models.CharField(max_length=139, blank=True, null=True)

    def __str__(self):
        return str(self.choice)
