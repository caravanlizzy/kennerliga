from datetime import datetime

from django.utils import timezone
from django.utils.timezone import now  # Use timezone-aware datetime
from django.core.validators import MinValueValidator, MaxValueValidator

from django.db import models
from user.models import PlayerProfile  # Assuming this is your participant model


# Create your models here.
class Season(models.Model):
    class SeasonStatus(models.TextChoices):
        NEXT = 'NEXT'
        OPEN = 'OPEN'
        RUNNING = 'RUNNING'
        DONE = 'DONE'

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
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def name(self) -> str:
        # zero-pad month if you like "2025_S10" vs "2025_S9"
        return f"{self.year}_S{self.month}"

    @property
    def season_start_time(self) -> datetime:
        # Build a naive dt for the first day of the month at 00:00
        dt = datetime(self.year, self.month, 1, 0, 0)
        # Make it timezone-aware using the project's default TZ
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_default_timezone())
        return dt

    @property
    def time_to_start(self):
        # Both operands are now aware -> safe subtraction
        return self.season_start_time - timezone.now()

    def __str__(self):
        return self.name


class SeasonParticipant(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='participants')
    profile = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='season_participants')
    rank = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('season', 'profile')
        ordering = ['rank']

    def __str__(self):
        return f"{self.profile.profile_name} - {self.season} (Rank: {self.rank})"
