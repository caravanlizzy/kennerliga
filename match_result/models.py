from django.db import models
from user.models import User


# Create your models here.
class MatchResult(models.Model):
    player = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
    )
    position = models.IntegerField(blank=True)
    points = models.IntegerField(blank=True)
    league = models.IntegerField(blank=True)
    season = models.IntegerField(blank=True)
    year = models.IntegerField(blank=True)
