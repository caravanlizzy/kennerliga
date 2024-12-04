from datetime import datetime
from django.utils.timezone import now  # Use timezone-aware datetime
from django.core.validators import MinValueValidator, MaxValueValidator

from django.db import models
from user.models import PlayerProfile  # Assuming this is your participant model


# Create your models here.
class Season(models.Model):
    class SeasonStatus(models.TextChoices):
        NEXT = 'Nächste'
        OPEN = 'Anmeldung offen'
        RUNNING = 'Laufend'
        DONE = 'Beendet'

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
        return self.season_start_time - now()

    def __str__(self):
        return self.name


class SeasonParticipant(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='participants')
    participant = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='season_participants')
    rank = models.IntegerField()

    class Meta:
        unique_together = ('season', 'participant')
        ordering = ['rank']

    def __str__(self):
        return f"{self.participant} - {self.season} (Rank: {self.rank})"
