from django.test import TestCase
from rest_framework.test import APIClient
from decimal import Decimal
from user.models import User, PlayerProfile, Platform
from season.models import Season, SeasonParticipant
from league.models import League, LeagueStatus, GameStanding
from league.services import (
    advance_turn,
    rotate_active_player,
    _format_ordinal,
    _format_points,
)
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

    def test_cannot_delete_league_with_results(self):
        client = APIClient()
        admin_user = User.objects.create_superuser(username="admin_del", password="pw")
        client.force_authenticate(user=admin_user)

        from result.models import Result
        sg = SelectedGame.objects.create(
            league=self.league, profile=self.profiles[0], game=self.games[0]
        )
        Result.objects.create(
            season=self.season,
            league=self.league,
            selected_game=sg,
            player_profile=self.profiles[0],
            points=10,
            position=1,
        )

        # League has_results should be True
        response = client.get(f"/api/league/leagues/{self.league.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["has_results"])

        # Deleting league should fail with 400
        del_response = client.delete(f"/api/league/leagues/{self.league.id}/")
        self.assertEqual(del_response.status_code, 400)
        self.assertIn("results already exist", del_response.data["detail"])
        self.assertTrue(League.objects.filter(id=self.league.id).exists())

    def test_can_delete_league_without_results(self):
        client = APIClient()
        admin_user = User.objects.create_superuser(username="admin_del2", password="pw")
        client.force_authenticate(user=admin_user)

        response = client.get(f"/api/league/leagues/{self.league.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["has_results"])

        del_response = client.delete(f"/api/league/leagues/{self.league.id}/")
        self.assertEqual(del_response.status_code, 204)
        self.assertFalse(League.objects.filter(id=self.league.id).exists())

    def test_cannot_remove_member_with_results_from_league(self):
        client = APIClient()
        admin_user = User.objects.create_superuser(username="admin_mem", password="pw")
        client.force_authenticate(user=admin_user)

        from result.models import Result
        sg = SelectedGame.objects.create(
            league=self.league, profile=self.profiles[0], game=self.games[0]
        )
        Result.objects.create(
            season=self.season,
            league=self.league,
            selected_game=sg,
            player_profile=self.profiles[0],
            points=10,
            position=1,
        )

        # Try to update league members to exclude profile[0] (self.participants[0])
        remaining_ids = [self.participants[1].id, self.participants[2].id]
        response = client.patch(
            f"/api/league/leagues/{self.league.id}/",
            {"member_ids": remaining_ids},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("member_ids", response.data)

    def test_cannot_add_participant_already_assigned_to_another_league(self):
        client = APIClient()
        admin_user = User.objects.create_superuser(username="admin_dup", password="pw")
        client.force_authenticate(user=admin_user)

        # self.participants are already in self.league (level 1)
        # Creating a new league (level 2) with participant[0] should fail
        response = client.post(
            "/api/league/leagues/",
            {
                "season": self.season.id,
                "level": 2,
                "member_ids": [self.participants[0].id],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("member_ids", response.data)

    def test_league_progress_tracking(self):
        from league.queries import get_league_progress
        from game.models import BanDecision
        from result.models import Result

        # 1. Initial state (4 players, 0 picks, 0 bans, 0 reports)
        prog = get_league_progress(self.league)
        self.assertEqual(prog["picks"], {"current": 0, "total": 4, "missing": 4})
        self.assertEqual(prog["bans"], {"current": 0, "total": 4, "missing": 4})
        self.assertEqual(prog["reports"], {"current": 0, "total": 4, "missing": 4})

        # 2. Add 2 picks
        sg1 = SelectedGame.objects.create(
            league=self.league, profile=self.profiles[0], game=self.games[0]
        )
        sg2 = SelectedGame.objects.create(
            league=self.league, profile=self.profiles[1], game=self.games[1]
        )
        prog = get_league_progress(self.league)
        self.assertEqual(prog["picks"], {"current": 2, "total": 4, "missing": 2})

        # 3. Complete initial 4 picks
        sg3 = SelectedGame.objects.create(
            league=self.league, profile=self.profiles[2], game=self.games[2]
        )
        sg4 = SelectedGame.objects.create(
            league=self.league, profile=self.profiles[3], game=self.games[3]
        )
        prog = get_league_progress(self.league)
        self.assertEqual(prog["picks"], {"current": 4, "total": 4, "missing": 0})
        self.assertEqual(prog["bans"], {"current": 0, "total": 4, "missing": 4})

        # 4. Add bans: 2 players ban sg1 (in 4-player league, 2 bans = success)
        BanDecision.objects.create(
            league=self.league,
            player_banning=self.profiles[0],
            selected_game=sg1,
        )
        BanDecision.objects.create(
            league=self.league,
            player_banning=self.profiles[1],
            selected_game=sg1,
        )
        # 2 more players ban nothing (pass/dummy ban or other)
        BanDecision.objects.create(
            league=self.league,
            player_banning=self.profiles[2],
            selected_game=None,
        )
        BanDecision.objects.create(
            league=self.league,
            player_banning=self.profiles[3],
            selected_game=None,
        )

        prog = get_league_progress(self.league)
        # All 4 players banned -> bans complete
        self.assertEqual(prog["bans"], {"current": 4, "total": 4, "missing": 0})
        # sg1 was profile 0's first pick and is banned -> profile 0 needs 1 repick -> total picks = 5
        self.assertEqual(prog["picks"], {"current": 4, "total": 5, "missing": 1})

        # 5. Add repick for profile 0
        extra_game = Game.objects.create(
            name="Extra Game", min_players=2, max_players=4, platform=self.platform
        )
        sg5 = SelectedGame.objects.create(
            league=self.league, profile=self.profiles[0], game=extra_game
        )
        prog = get_league_progress(self.league)
        self.assertEqual(prog["picks"], {"current": 5, "total": 5, "missing": 0})
        self.assertEqual(prog["reports"], {"current": 0, "total": 4, "missing": 4})

        # 6. Report results for sg2 (playable game) for all 4 players
        for prof in self.profiles:
            Result.objects.create(
                season=self.season,
                league=self.league,
                selected_game=sg2,
                player_profile=prof,
                points=10,
                position=1,
            )

        prog = get_league_progress(self.league)
        self.assertEqual(prog["reports"], {"current": 1, "total": 4, "missing": 3})

        # 7. Test via API client list endpoint
        client = APIClient()
        client.force_authenticate(user=self.users[0])
        response = client.get(f"/api/league/leagues/?season={self.season.id}")
        self.assertEqual(response.status_code, 200)
        league_data = next(
            item for item in response.data if item["id"] == self.league.id
        )
        self.assertIn("progress", league_data)
        self.assertEqual(league_data["progress"]["picks"]["missing"], 0)
        self.assertEqual(league_data["progress"]["bans"]["missing"], 0)
        self.assertEqual(league_data["progress"]["reports"]["current"], 1)
        self.assertEqual(league_data["progress"]["reports"]["missing"], 3)
