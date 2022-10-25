from django.db import models
from user.models import User


# Create your models here.
class Season(models.Model):
    participants = models.ManyToManyField(User,
        blank=True,
        null=True,
    )
    year = models.IntegerField()
    number = models.IntegerField(
        'month in the current year'
    )
    registration_open = models.BooleanField()

    def __str__(self):
        return f'S{self.number}'

    def create_leagues(self, season_pk):
        self.objects.filter(pk=season_number)

    def get_player_order(self, season_number):
        participants = self.objects.filter(number=season_number).participants.all()

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
