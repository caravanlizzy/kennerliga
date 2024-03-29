from django.db import models
from user.models import User
from season.models import Season


# Create your models here.
class League(models.Model):
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    level = models.IntegerField('1 for L1, 2 for L2 etc.')
    members = models.ManyToManyField(User, related_name='leagues_member')

    def __str__(self):
        return f'{self.season}L{self.number}'
