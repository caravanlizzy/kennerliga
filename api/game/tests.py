from django.test import TestCase
from rest_framework.test import APIClient
from user.models import User, PlayerProfile, Platform
from season.models import Season, SeasonParticipant
from league.models import League, LeagueStatus
from game.models import (
    Game,
    SelectedGame,
    ResultConfig,
    StartingPointSystem,
    BanDecision,
)


class GameAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username="admin", password="password")
        self.client.force_authenticate(user=self.user)

        self.platform = Platform.objects.create(name="BGA")
        self.season = Season.objects.create(
            year=2026, month=1, status=Season.SeasonStatus.RUNNING
        )
        self.profile = PlayerProfile.objects.create(
            user=self.user, profile_name="Admin Profile"
        )
        self.participant = SeasonParticipant.objects.create(
            season=self.season, profile=self.profile, rank=1
        )

        self.league = League.objects.create(
            season=self.season, level=1, status=LeagueStatus.PICKING
        )
        self.league.members.add(self.participant)
        self.league.active_player = self.participant
        self.league.save()

        self.sps = StartingPointSystem.objects.create(
            id=1, code="FIXED", description="Fixed points"
        )
        self.game = Game.objects.create(
            name="Catan", min_players=1, max_players=4, platform=self.platform
        )
        ResultConfig.objects.create(
            game=self.game, has_points=True, starting_points_system=self.sps
        )

    def test_get_games(self):
        response = self.client.get("/api/game/games/")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)

    def test_filter_games_for_selection(self):
        # Create a game that should not be used for selection
        game2 = Game.objects.create(
            name="Old Game",
            min_players=1,
            max_players=4,
            platform=self.platform,
            selectable=False,
        )

        # Regular request
        response = self.client.get("/api/game/games/")
        self.assertEqual(response.status_code, 200)
        game_names = [g["name"] for g in response.data]
        self.assertIn("Catan", game_names)
        self.assertNotIn("Old Game", game_names)

        # Admin request with manage_only=true
        response = self.client.get("/api/game/games/?manage_only=true")
        self.assertEqual(response.status_code, 200)
        game_names = [g["name"] for g in response.data]
        self.assertIn("Catan", game_names)
        self.assertIn("Old Game", game_names)

    def test_select_game(self):
        data = {
            "game": self.game.id,
            "league": self.league.id,
            "profile": self.profile.id,
            "selected_options": [],
        }
        response = self.client.post("/api/game/selected-games/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(SelectedGame.objects.count(), 1)
        self.assertTrue(response.data["is_selectable"])

        # Select another game
        game2 = Game.objects.create(
            name="Catan 2", min_players=1, max_players=4, platform=self.platform
        )
        data["game"] = game2.id
        response = self.client.post("/api/game/selected-games/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["is_selectable"])

        # Check the first game again - it should NOT be selectable anymore
        first_game_id = SelectedGame.objects.order_by("id").first().id
        response = self.client.get(f"/api/game/selected-games/{first_game_id}/")
        self.assertFalse(response.data["is_selectable"])

        self.league.refresh_from_db()
        self.assertEqual(self.league.status, LeagueStatus.BANNING)

    def test_create_ban_decision(self):
        data = {
            "player_banning": self.profile.id,
            "league": self.league.id,
            "selected_game_id": None,
        }
        response = self.client.post("/api/game/ban-decisions/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(BanDecision.objects.count(), 1)

    def test_create_result_config_nested(self):
        new_game = Game.objects.create(
            name="Terraforming Mars", min_players=1, max_players=5, platform=self.platform
        )
        payload = {
            "game": new_game.id,
            "is_asymmetric": True,
            "has_starting_player_order": True,
            "has_points": True,
            "starting_points_system": self.sps.id,
            "factions": [
                {"name": "Ecoline", "level": 0},
                {"name": "Tharsis", "level": 0},
            ],
            "win_conditions": [
                {
                    "name": "Victory Points",
                    "condition_type": "POINTS",
                    "order": 0,
                    "tie_breakers": [
                        {"name": "Megacredits", "higher_wins": True, "order": 10}
                    ],
                },
                {
                    "name": "Corporate Era",
                    "condition_type": "OPTION",
                    "order": 10,
                    "options": [
                        {"name": "Standard", "order": 0},
                        {"name": "Draft", "order": 10},
                    ],
                },
            ],
        }
        response = self.client.post("/api/game/result-configs/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("factions", response.data)
        self.assertEqual(len(response.data["factions"]), 2)
        self.assertEqual(len(response.data["win_conditions"]), 2)

        # Retrieve and verify nested data
        config_id = response.data["id"]
        get_res = self.client.get(f"/api/game/result-configs/{config_id}/")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(len(get_res.data["factions"]), 2)
        self.assertEqual(len(get_res.data["win_conditions"]), 2)
        self.assertEqual(len(get_res.data["win_conditions"][0]["tie_breakers"]), 1)
        self.assertEqual(len(get_res.data["win_conditions"][1]["options"]), 2)

    def test_update_result_config_nested(self):
        existing_config = ResultConfig.objects.filter(game=self.game).first()
        payload = {
            "is_asymmetric": False,
            "factions": [
                {"name": "Red", "level": 0},
                {"name": "Blue", "level": 0},
                {"name": "Green", "level": 0},
            ],
            "win_conditions": [
                {
                    "name": "Points",
                    "condition_type": "POINTS",
                    "order": 0,
                    "tie_breakers": [
                        {"name": "Resources", "higher_wins": True, "order": 10}
                    ],
                }
            ],
        }
        response = self.client.patch(
            f"/api/game/result-configs/{existing_config.id}/", payload, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["factions"]), 3)
        self.assertEqual(len(response.data["win_conditions"]), 1)
        self.assertEqual(len(response.data["win_conditions"][0]["tie_breakers"]), 1)

    def test_create_result_config_default_win_condition(self):
        new_game = Game.objects.create(
            name="Wingspan", min_players=1, max_players=5, platform=self.platform
        )
        payload = {
            "game": new_game.id,
            "has_points": True,
            "starting_points_system": self.sps.id,
        }
        response = self.client.post("/api/game/result-configs/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data["win_conditions"]), 1)
        self.assertEqual(response.data["win_conditions"][0]["name"], "Points")
        self.assertEqual(response.data["win_conditions"][0]["condition_type"], "POINTS")
