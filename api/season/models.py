from datetime import datetime

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# Create your models here.
class Season(models.Model):
    class SeasonStatus(models.TextChoices):
        NEXT = 'Nächste'
        OPEN = 'Anmeldung offen'
        RUNNING = 'Laufend'
        DONE = 'Beendet'

    participants = models.ManyToManyField(
        'user.PlayerProfile',  # lazy reference to avoid circular imports
        blank=True,
        related_name='seasons_participating'
    )
    year = models.IntegerField()
    month = models.IntegerField(
        'month in the current year',
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    status = models.CharField(
        max_length=15,
        choices=SeasonStatus.choices,
        default=SeasonStatus.NEXT
    )

    @property
    def name(self):
        return str(self.year) + '_S' + str(self.month)

    @property
    def season_start_time(self):
        return datetime(self.year, self.month, 1, 0, 0)

    @property
    def time_to_start(self):
        return self.season_start_time - datetime.now()

    def __str__(self):
        return self.name
