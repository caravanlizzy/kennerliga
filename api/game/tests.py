from django.test import TestCase
from rest_framework.test import APIClient
from user.models import User, PlayerProfile, Platform
from season.models import Season, SeasonParticipant
from league.models import League, LeagueStatus
from game.models import (
    Game,
    GameOption,
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

    def test_delete_ban_decision(self):
        ban_decision = BanDecision.objects.create(
            player_banning=self.profile,
            league=self.league,
            skipped_ban=True,
        )
        self.assertEqual(BanDecision.objects.count(), 1)
        response = self.client.delete(f"/api/game/ban-decisions/{ban_decision.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(BanDecision.objects.count(), 0)

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
                {"name": "Prelude Leader A", "level": 1},
                {"name": "Colony Policy B", "level": 2},
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
        self.assertEqual(len(response.data["factions"]), 4)
        self.assertEqual(len(response.data["win_conditions"]), 2)

        # Retrieve and verify nested data including faction levels
        config_id = response.data["id"]
        get_res = self.client.get(f"/api/game/result-configs/{config_id}/")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(len(get_res.data["factions"]), 4)
        levels_map = {f["name"]: f["level"] for f in get_res.data["factions"]}
        self.assertEqual(levels_map["Ecoline"], 0)
        self.assertEqual(levels_map["Tharsis"], 0)
        self.assertEqual(levels_map["Prelude Leader A"], 1)
        self.assertEqual(levels_map["Colony Policy B"], 2)

        # Verify factions endpoint returns levels correctly
        factions_res = self.client.get(f"/api/game/factions/?game={new_game.id}")
        self.assertEqual(factions_res.status_code, 200)
        f_levels_map = {f["name"]: f["level"] for f in factions_res.data}
        self.assertEqual(f_levels_map["Prelude Leader A"], 1)
        self.assertEqual(f_levels_map["Colony Policy B"], 2)

        self.assertEqual(len(get_res.data["win_conditions"]), 2)
        self.assertEqual(len(get_res.data["win_conditions"][0]["tie_breakers"]), 1)
        self.assertEqual(len(get_res.data["win_conditions"][1]["options"]), 2)

    def test_update_result_config_nested(self):
        existing_config = ResultConfig.objects.filter(game=self.game).first()
        payload = {
            "is_asymmetric": True,
            "factions": [
                {"name": "Red", "level": 0},
                {"name": "Blue", "level": 1},
                {"name": "Green", "level": 2},
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
        levels_map = {f["name"]: f["level"] for f in response.data["factions"]}
        self.assertEqual(levels_map["Red"], 0)
        self.assertEqual(levels_map["Blue"], 1)
        self.assertEqual(levels_map["Green"], 2)
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

    def test_get_and_create_platforms(self):
        # Fetch platforms
        res = self.client.get("/api/game/platforms/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

        # Create new platform as admin
        create_res = self.client.post(
            "/api/game/platforms/", {"name": "Steam"}, format="json"
        )
        self.assertEqual(create_res.status_code, 201)
        self.assertEqual(create_res.data["name"], "Steam")

        # Verify list contains new platform
        res = self.client.get("/api/game/platforms/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 2)

    def test_selected_game_serialization_and_has_results_filter(self):
        from result.models import Result
        selected_game = SelectedGame.objects.create(
            game=self.game,
            league=self.league,
            profile=self.profile,
        )

        # Initially selected_game has no results
        res = self.client.get("/api/game/selected-games/?has_results=true")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 0)

        # Create a result for selected_game
        Result.objects.create(
            season=self.season,
            league=self.league,
            selected_game=selected_game,
            player_profile=self.profile,
            points=100,
            position=1,
        )

        res = self.client.get("/api/game/selected-games/?has_results=true")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        item = res.data[0]
        self.assertEqual(item["id"], selected_game.id)
        self.assertEqual(item["season_id"], self.season.id)
        self.assertEqual(item["season_name"], self.season.name)
        self.assertEqual(item["league_level"], self.league.level)
        self.assertEqual(item["league"], self.league.id)
        self.assertEqual(len(item["results"]), 1)

        # Test season filter
        res_season = self.client.get(f"/api/game/selected-games/?season={self.season.id}")
        self.assertEqual(res_season.status_code, 200)
        self.assertEqual(len(res_season.data), 1)

    def test_full_game_create_related_games(self):
        steam = Platform.objects.create(name="Steam")
        related_game = Game.objects.create(name="Catan", platform=steam)

        response = self.client.post(
            "/api/game/games-full/",
            {
                "name": "Catan Online",
                "platform": self.platform.id,
                "related_games": [related_game.id],
                "options": [],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        created_game = Game.objects.get(id=response.data["id"])
        self.assertEqual(
            list(created_game.related_games.values_list("id", flat=True)),
            [related_game.id],
        )
        self.assertEqual(response.data["related_games"], [related_game.id])
        self.assertIn(created_game, related_game.related_games.all())

    def test_full_game_related_games_can_be_read_updated_and_removed(self):
        related_game = Game.objects.create(name="Catan Online", platform=self.platform)
        self.game.related_games.add(related_game)
        option = GameOption.objects.create(name="Map", game=self.game)

        for game in (self.game, related_game):
            response = self.client.get(
                f"/api/game/games-full/{game.id}/?manage_only=true"
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["related_games"], [
                related_game.id if game == self.game else self.game.id
            ])

        omitted_response = self.client.patch(
            f"/api/game/games-full/{self.game.id}/",
            {"name": "Catan Revised"},
            format="json",
        )
        self.assertEqual(omitted_response.status_code, 200)
        self.assertIn(related_game, self.game.related_games.all())
        self.assertTrue(GameOption.objects.filter(id=option.id).exists())

        clear_response = self.client.patch(
            f"/api/game/games-full/{self.game.id}/",
            {"related_games": []},
            format="json",
        )
        self.assertEqual(clear_response.status_code, 200)
        self.assertFalse(self.game.related_games.exists())
        self.assertFalse(related_game.related_games.exists())
        self.assertTrue(GameOption.objects.filter(id=option.id).exists())

    def test_full_game_rejects_invalid_and_self_related_game_ids(self):
        invalid_response = self.client.post(
            "/api/game/games-full/",
            {
                "name": "Invalid Link",
                "platform": self.platform.id,
                "related_games": [999999],
                "options": [],
            },
            format="json",
        )
        self.assertEqual(invalid_response.status_code, 400)

        self_related_response = self.client.patch(
            f"/api/game/games-full/{self.game.id}/",
            {"related_games": [self.game.id]},
            format="json",
        )
        self.assertEqual(self_related_response.status_code, 400)
        self.assertFalse(self.game.related_games.exists())

    def test_full_game_create_rolls_back_related_links_on_invalid_options(self):
        initial_count = Game.objects.count()
        response = self.client.post(
            "/api/game/games-full/",
            {
                "name": "Invalid Options",
                "platform": self.platform.id,
                "related_games": [self.game.id],
                "options": [
                    {"name": "First", "ref": "duplicate"},
                    {"name": "Second", "ref": "duplicate"},
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Game.objects.count(), initial_count)
        self.assertFalse(self.game.related_games.exists())

    def test_full_game_update_rolls_back_related_links_on_invalid_options(self):
        steam = Platform.objects.create(name="Steam")
        existing_related_game = Game.objects.create(name="Catan Online", platform=steam)
        new_related_game = Game.objects.create(name="Catan Digital", platform=steam)
        self.game.related_games.add(existing_related_game)

        response = self.client.patch(
            f"/api/game/games-full/{self.game.id}/",
            {
                "related_games": [new_related_game.id],
                "options": [
                    {"name": "First", "ref": "duplicate"},
                    {"name": "Second", "ref": "duplicate"},
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            list(self.game.related_games.values_list("id", flat=True)),
            [existing_related_game.id],
        )
        self.assertFalse(new_related_game.related_games.exists())
        self.assertFalse(GameOption.objects.filter(game=self.game).exists())

    def test_related_game_picks_share_the_per_year_limit(self):
        steam = Platform.objects.create(name="Steam")
        related_game = Game.objects.create(
            name="Catan Online", platform=steam, min_players=1, max_players=4
        )
        self.game.related_games.add(related_game)

        second_league = League.objects.create(
            season=self.season, level=2, status=LeagueStatus.PICKING
        )
        third_league = League.objects.create(
            season=self.season, level=3, status=LeagueStatus.PICKING
        )
        for league in (self.league, second_league, third_league):
            league.members.add(self.participant)

        SelectedGame.objects.create(
            profile=self.profile, game=self.game, league=self.league
        )
        SelectedGame.objects.create(
            profile=self.profile, game=self.game, league=second_league
        )

        response = self.client.post(
            "/api/game/selected-games/",
            {
                "game": related_game.id,
                "league": third_league.id,
                "profile": self.profile.id,
                "selected_options": [],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(SelectedGame.objects.count(), 2)
