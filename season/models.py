from django.db import models

from user.models import User


# Create your models here.
class Season(models.Model):
    class SeasonStatus(models.TextChoices):
        ANNOUNCED = 'Angekündigt'
        OPEN = 'Anmeldung offen'
        DONE = 'Beendet'

    participants = models.ManyToManyField(
        User,
        blank=True,
        null=True,
        related_name='seasons_participating'
    )
    year = models.IntegerField()
    month = models.IntegerField(
        'month in the current year'
    )
    status = models.CharField(
        max_length=15,
        choices=SeasonStatus.choices,
        default=SeasonStatus.DONE
    )

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

# class Registration(models.Model):
#     player = models.ManyToManyField(
#         User,
#     )
#     season = models.ForeignKey(
#         Season,
#         on_delete=models.CASCADE,
#     )
#     datetime = models.DateTimeField(auto_now_add=True, editable=False)
