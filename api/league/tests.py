from django.test import TestCase
from user.models import User, PlayerProfile, Platform
from season.models import Season, SeasonParticipant
from league.models import League, LeagueStatus
from league.services import advance_turn, rotate_active_player
from game.models import Game, SelectedGame
from api.constants import get_game_picks_per_player

class LeagueServiceTests(TestCase):
    def setUp(self):
        self.season = Season.objects.create(year=2026, month=1, status=Season.SeasonStatus.RUNNING)
        self.platform = Platform.objects.create(name='BGA')
        self.users = []
        self.profiles = []
        self.participants = []
        for i in range(4):
            user = User.objects.create(username=f'user{i}')
            profile = PlayerProfile.objects.create(user=user, profile_name=f'profile{i}')
            participant = SeasonParticipant.objects.create(season=self.season, profile=profile, rank=i+1)
            self.users.append(user)
            self.profiles.append(profile)
            self.participants.append(participant)
        
        self.league = League.objects.create(season=self.season, level=1, status=LeagueStatus.PICKING)
        for p in self.participants:
            self.league.members.add(p)
        self.league.active_player = self.participants[0]
        self.league.save()
        
        self.games = [
            Game.objects.create(name=f'Game {i}', min_players=2, max_players=4, platform=self.platform)
            for i in range(4)
        ]

    def test_rotate_active_player(self):
        self.assertEqual(self.league.active_player, self.participants[0])
        next_player = rotate_active_player(self.league)
        self.assertEqual(next_player, self.participants[1])
        self.assertEqual(self.league.active_player, self.participants[1])

    def test_advance_turn_picking_to_banning(self):
        # In a 4 player league, each player picks 1 game (per get_game_picks_per_player)
        picks_needed = get_game_picks_per_player(4)
        self.assertEqual(picks_needed, 1)
        
        for i in range(4):
            self.assertEqual(self.league.active_player, self.participants[i])
            SelectedGame.objects.create(league=self.league, profile=self.profiles[i], game=self.games[i])
            advance_turn(self.league)
            
        self.assertEqual(self.league.status, LeagueStatus.BANNING)
        # Should be back to first player for banning
        self.assertEqual(self.league.active_player, self.participants[0])
