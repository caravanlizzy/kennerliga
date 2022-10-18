from django.db import models


# Create your models here.
class Game(models.Model):
    name = models.CharField(max_length=88)


class GameOptionCategory(models.Model):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    category = models.CharField(max_length=88)
    type = models.BooleanField()  # booleanOption or MultipleOptions


class GameOption(models.Model):
    category = models.ForeignKey(
        GameOptionCategory,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    option = models.CharField(max_length=139)

