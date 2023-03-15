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
    is_bool = models.BooleanField()  # booleanOption or MultipleOptions

    def __str__(self):
        return str(self.name)


class GameSettingsOption(models.Model):
    category = models.ForeignKey(
        GameSettingsCategory,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='options'
    )
    option = models.CharField(max_length=139)

    def __str__(self):
        return str(self.option)


class GameSettingsOptionBool(models.Model):
    category = models.ForeignKey(
        GameSettingsCategory,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    option = models.BooleanField()
