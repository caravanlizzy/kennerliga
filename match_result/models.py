from django.db import models
from user.models import User


# Create your models here.
class MatchResult(models.Model):
    player = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    position = models.IntegerField()
    points = models.IntegerField()
    league = models.IntegerField()
    season = models.IntegerField()
    year = models.IntegerField()
