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
    position = models.IntegerField(blank=True, null=True)
    points = models.IntegerField(blank=True, null=True)
    league = models.IntegerField(blank=True, null=True)
    season = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
