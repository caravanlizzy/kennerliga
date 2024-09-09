from datetime import datetime

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from user.models import PlayerProfile


# Create your models here.
class Season(models.Model):
    class SeasonStatus(models.TextChoices):
        NEXT = 'Nächste'
        OPEN = 'Anmeldung offen'
        RUNNING = 'Laufend'
        DONE = 'Beendet'

    participants = models.ManyToManyField(
        PlayerProfile,
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

    def get_running_season(self):
        return self.objects.filter(status=Season.SeasonStatus.RUNNING).first()

    def get_open_season(self):
        return self.objects.filter(status=Season.SeasonStatus.OPEN).first()

    def get_previous_season(self):
        return self.objects.filter(status=Season.SeasonStatus.DONE).last()

    def get_participants(self, season_name):
        return self.objects.filter(year=season_name).participants.all()

    def get_registered_participant_count(self):
        season = self.get_open_season()
        if season:
            return season.participants.count()
        else:
            print("No open season found.")
            return 0

    def get_registered_participants(self):
        season = self.get_open_season()
        if season:
            return season.participants.all()
        else:
            print("No open season found.")
            return []

    def __str__(self):
        return self.name
