from django.test import TestCase
from rest_framework.test import APIClient
from decimal import Decimal
from user.models import User, PlayerProfile, Platform
from season.models import Season, SeasonParticipant
from league.models import League, LeagueStatus, GameStanding, LeagueStanding
from league.services import (
    advance_turn,
    rotate_active_player,
    _format_ordinal,
    _format_points,
)
from league.serializer import GameStandingSerializer
from game.models import Game, SelectedGame, ResultConfig, StartingPointSystem
from api.constants import get_game_picks_per_player


class LeagueServiceTests(TestCase):
    def setUp(self):
        self.season = Season.objects.create(
            year=2026, month=1, status=Season.SeasonStatus.RUNNING
        )
        self.platform = Platform.objects.create(name="BGA")
        self.users = []
        self.profiles = []
        self.participants = []
        for i in range(4):
            user = User.objects.create(username=f"user{i}")
            profile = PlayerProfile.objects.create(
                user=user, profile_name=f"profile{i}"
            )
            participant = SeasonParticipant.objects.create(
                season=self.season, profile=profile, rank=i + 1
            )
            self.users.append(user)
            self.profiles.append(profile)
            self.participants.append(participant)

        self.league = League.objects.create(
            season=self.season, level=1, status=LeagueStatus.PICKING
        )
        for p in self.participants:
            self.league.members.add(p)
        self.league.active_player = self.participants[0]
        self.league.save()

        self.games = [
            Game.objects.create(
                name=f"Game {i}", min_players=2, max_players=4, platform=self.platform
            )
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
            SelectedGame.objects.create(
                league=self.league, profile=self.profiles[i], game=self.games[i]
            )
            advance_turn(self.league)

        self.assertEqual(self.league.status, LeagueStatus.BANNING)
        # Should be back to first player for banning
        self.assertEqual(self.league.active_player, self.participants[0])

    def test_format_helpers(self):
        self.assertEqual(_format_ordinal(1), "1st")
        self.assertEqual(_format_ordinal(2), "2nd")
        self.assertEqual(_format_ordinal(3), "3rd")
        self.assertEqual(_format_ordinal(4), "4th")
        self.assertEqual(_format_ordinal(11), "11th")
        self.assertEqual(_format_ordinal(21), "21st")
        self.assertIsNone(_format_ordinal(None))

        self.assertEqual(_format_points(45.00), "45")
        self.assertEqual(_format_points(Decimal("45.50")), "45.5")
        self.assertIsNone(_format_points(None))

    def test_full_standings_display_fields(self):
        client = APIClient()
        admin_user = User.objects.create_superuser(username="admin_s", password="pw")
        client.force_authenticate(user=admin_user)

        sps = StartingPointSystem.objects.create(
            id=10, code="FIXED", description="Fixed points"
        )
        # Game with points
        ResultConfig.objects.create(
            game=self.games[0], has_points=True, starting_points_system=sps
        )
        # Game without points (placement based)
        ResultConfig.objects.create(
            game=self.games[1], has_points=False, starting_points_system=sps
        )

        sg1 = SelectedGame.objects.create(
            league=self.league, profile=self.profiles[0], game=self.games[0]
        )
        sg2 = SelectedGame.objects.create(
            league=self.league, profile=self.profiles[1], game=self.games[1]
        )

        # Standings for sg1 (points)
        GameStanding.objects.create(
            league=self.league,
            selected_game=sg1,
            player_profile=self.profiles[0],
            points=Decimal("52.5"),
            rank=1,
            league_points=Decimal("25"),
        )
        # Standings for sg2 (position/no points: stored as -1)
        GameStanding.objects.create(
            league=self.league,
            selected_game=sg2,
            player_profile=self.profiles[0],
            points=Decimal("-1.0"),
            rank=1,
            league_points=Decimal("25"),
        )

        response = client.get(
            f"/api/league/leagues/{self.league.id}/full-standings/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("is_season_completed", response.data)
        self.assertFalse(response.data["is_season_completed"])

        standings = response.data["standings"]
        p0_row = next(
            s for s in standings if s["player_profile_id"] == self.profiles[0].id
        )

        # sg1 has_points=True -> display_value should be "52.5", display_rank="1st"
        self.assertEqual(p0_row["games"][str(sg1.id)]["display_value"], "52.5")
        self.assertEqual(p0_row["games"][str(sg1.id)]["display_rank"], "1st")
        self.assertEqual(p0_row["games"][str(sg1.id)]["rank"], 1)

        # sg2 has_points=False -> display_value should be "1st", display_rank="1st"
        self.assertEqual(p0_row["games"][str(sg2.id)]["display_value"], "1st")
        self.assertEqual(p0_row["games"][str(sg2.id)]["display_rank"], "1st")
        self.assertEqual(p0_row["games"][str(sg2.id)]["rank"], 1)
