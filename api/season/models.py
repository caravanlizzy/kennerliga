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
    def season_start_time(self):
        return datetime(self.year, self.month, 1, 0, 0)

    @property
    def time_to_start(self):
        return self.season_start_time - datetime.now()

    def __str__(self):
        return f'{self.year}_S{self.month}'

    def create_leagues(self):
        pass

    def get_player_order(self, season_number):
        participants = self.objects.filter(number=season_number).participants.all()

    @staticmethod
    def get_players_per_league(self, participants_amount):
        rest_players = participants_amount % 4
        league_amount = participants_amount // 4 + 1 if rest_players > 0 else participants_amount // 4
        for league in range(league_amount):
            players_per_league = league_amount * [4]
        if rest_players == 1:
            players_per_league[-1] = 2
            players_per_league[-2] = 3
        elif rest_players == 2:
            players_per_league[-1] = 2
        elif rest_players == 3:
            players_per_league[-1] = 3
        return players_per_league


def get_current_season():
    return Season.objects.order_by('-year', '-month').first()


def get_new_month_year(month, year):
    new_month = month + 1
    new_year = year
    if new_month == 13:
        new_year += 1
        new_month = 1
    return [new_month, new_year]


def create_season():
    current_season = get_current_season()
    if not current_season:
        print("No seasons created so far.")
        return
    new_month, new_year = get_new_month_year(current_season.month, current_season.year)
    new_season = Season(year=new_year, month=new_month)
    new_season.save()

# class Registration(models.Model):
#     player = models.ManyToManyField(
#         User,
#     )
#     season = models.ForeignKey(
#         Season,
#         on_delete=models.CASCADE,
#     )
#     datetime = models.DateTimeField(auto_now_add=True, editable=False)
