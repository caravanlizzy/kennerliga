from django.db import models
from user.models import User

# Create your models here.
class Season(models.Model):
    participant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    year = models.DateField()
    number = models.IntegerField(
        'number between 1 and 12 - month of the current season'
    )
