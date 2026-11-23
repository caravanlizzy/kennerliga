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
from services.scoring import Row, compute_league_table
from unittest.mock import patch


class LeaguePlacementScoringTests(TestCase):
    def test_second_and_third_places_break_ties_before_raw_points(self):
        rows = [
            Row(1, 1, "A", 100, 2), Row(1, 2, "B", 1, 3),
            Row(2, 1, "A", 100, 4), Row(2, 2, "B", 1, 2),
            Row(3, 1, "A", 100, 3), Row(3, 2, "B", 1, 4),
            Row(4, 1, "A", 100, 4), Row(4, 2, "B", 1, 3),
            Row(5, 1, "A", 100, 4), Row(5, 2, "B", 1, 3),
        ]
        for game_id in range(1, 6):
            occupied = {r.position for r in rows if r.selected_game_id == game_id}
            for position in set(range(1, 5)) - occupied:
                rows.append(Row(game_id, 10 + game_id * 4 + position, "X", 0, position))
        table = compute_league_table(rows, place_points={})
        players = [r for r in table if r["player_id"] in (1, 2)]
        self.assertEqual([r["player_id"] for r in players], [2, 1])
        self.assertEqual([(r["second_places"], r["third_places"]) for r in players], [(1, 3), (1, 1)])

    def test_tied_placements_count_for_each_player(self):
        rows = [Row(1, 1, "A", 0, 1), Row(1, 2, "B", 0, 2),
                Row(1, 3, "C", 0, 2), Row(1, 4, "D", 0, 4)]
        table = compute_league_table(rows)
        by_player = {row["player_id"]: row for row in table}
        self.assertEqual(by_player[2]["second_places"], 1)
        self.assertEqual(by_player[3]["second_places"], 1)
        self.assertEqual(by_player[2]["third_places"], 0)


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

    def test_snapshot_and_display_use_all_tie_break_criteria(self):
        from league.models import LeagueStanding
        from league.services import get_full_standings_data
        from services.standings_snapshot import rebuild_league_snapshot

        table = [
            {"player_id": profile.id, "league_points": Decimal("10"),
             "wins": Decimal("1"), "second_places": seconds, "third_places": thirds}
            for profile, seconds, thirds in zip(self.profiles, [0, 1, 1, 1], [0, 0, 1, 1])
        ]
        with patch("services.standings_snapshot.compute_league_table", return_value=table):
            rebuild_league_snapshot(self.league)

        standings = {s.player_profile_id: s for s in LeagueStanding.objects.filter(league=self.league)}
        self.assertIsNone(standings[self.profiles[0].id].unresolved_tie_group)
        self.assertIsNone(standings[self.profiles[1].id].unresolved_tie_group)
        self.assertEqual(standings[self.profiles[2].id].unresolved_tie_group,
                         standings[self.profiles[3].id].unresolved_tie_group)
        self.assertIsNotNone(standings[self.profiles[2].id].unresolved_tie_group)
        data = get_full_standings_data(self.league)
        self.assertEqual([row["player_profile_id"] for row in data["standings"]],
                         [self.profiles[i].id for i in [2, 3, 1, 0]])
        self.assertEqual(len(data["tie_groups"]), 1)

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

    def test_resolve_tie_permissions_and_resolution(self):
        from league.models import LeagueStanding, LeagueTieResolution, TieResolutionReason
        from services.standings_snapshot import rebuild_league_snapshot

        # Set up a tie between profiles[0] and profiles[1]
        table = [
            {
                "player_id": self.profiles[0].id,
                "league_points": Decimal("10"),
                "wins": Decimal("2"),
                "second_places": 1,
                "third_places": 0,
            },
            {
                "player_id": self.profiles[1].id,
                "league_points": Decimal("10"),
                "wins": Decimal("2"),
                "second_places": 1,
                "third_places": 0,
            },
            {
                "player_id": self.profiles[2].id,
                "league_points": Decimal("6"),
                "wins": Decimal("1"),
                "second_places": 0,
                "third_places": 1,
            },
            {
                "player_id": self.profiles[3].id,
                "league_points": Decimal("2"),
                "wins": Decimal("0"),
                "second_places": 0,
                "third_places": 0,
            },
        ]
        with patch("services.standings_snapshot.compute_league_table", return_value=table):
            rebuild_league_snapshot(self.league)

        standings = {s.player_profile_id: s for s in LeagueStanding.objects.filter(league=self.league)}
        group_key = standings[self.profiles[0].id].unresolved_tie_group
        self.assertIsNotNone(group_key)
        self.assertEqual(standings[self.profiles[1].id].unresolved_tie_group, group_key)

        client = APIClient()

        payload = {
            "group_key": group_key,
            "reason": TieResolutionReason.CANT_STOP,
            "player_order": [self.profiles[1].id, self.profiles[0].id],
            "note": "Played tie-breaker match",
        }

        # 1. Unauthenticated request -> 401
        res = client.post(f"/api/league/leagues/{self.league.id}/resolve-tie/", payload, format="json")
        self.assertEqual(res.status_code, 401)

        # 2. Non-member user -> 403
        outsider_user = User.objects.create(username="outsider")
        client.force_authenticate(user=outsider_user)
        res = client.post(f"/api/league/leagues/{self.league.id}/resolve-tie/", payload, format="json")
        self.assertEqual(res.status_code, 403)

        # 3. League member who is NOT in the tie group (e.g. users[2] / profiles[2]) -> 403
        client.force_authenticate(user=self.users[2])
        res = client.post(f"/api/league/leagues/{self.league.id}/resolve-tie/", payload, format="json")
        self.assertEqual(res.status_code, 403)
        self.assertIn("Only players who are part of this tie group", res.data["detail"])

        # 4. League member player who IS in the tie group (e.g. users[0] / profiles[0]) -> 200 OK
        client.force_authenticate(user=self.users[0])
        res = client.post(f"/api/league/leagues/{self.league.id}/resolve-tie/", payload, format="json")
        self.assertEqual(res.status_code, 200)

        # Verify standings updated: unresolved_tie_group cleared, priorities assigned
        s0 = LeagueStanding.objects.get(league=self.league, player_profile=self.profiles[0])
        s1 = LeagueStanding.objects.get(league=self.league, player_profile=self.profiles[1])
        self.assertIsNone(s0.unresolved_tie_group)
        self.assertIsNone(s1.unresolved_tie_group)
        self.assertGreater(s1.tie_break_priority, s0.tie_break_priority)

        # Verify LeagueTieResolution recorded
        resolution = LeagueTieResolution.objects.get(league=self.league, group_key=group_key)
        self.assertTrue(resolution.is_resolved)
        self.assertEqual(resolution.reason, TieResolutionReason.CANT_STOP)
        self.assertEqual(resolution.note, "Played tie-breaker match")

    def test_admin_tie_resolution_viewset_crud(self):
        from league.models import LeagueStanding, LeagueTieResolution, TieResolutionReason
        from services.standings_snapshot import rebuild_league_snapshot

        # Create standings with a tie between profiles[0] and profiles[1]
        table = [
            {
                "player_id": self.profiles[0].id,
                "league_points": Decimal("10"),
                "wins": Decimal("2"),
                "second_places": 1,
                "third_places": 0,
            },
            {
                "player_id": self.profiles[1].id,
                "league_points": Decimal("10"),
                "wins": Decimal("2"),
                "second_places": 1,
                "third_places": 0,
            },
            {
                "player_id": self.profiles[2].id,
                "league_points": Decimal("6"),
                "wins": Decimal("1"),
                "second_places": 0,
                "third_places": 1,
            },
            {
                "player_id": self.profiles[3].id,
                "league_points": Decimal("2"),
                "wins": Decimal("0"),
                "second_places": 0,
                "third_places": 0,
            },
        ]
        with patch("services.standings_snapshot.compute_league_table", return_value=table):
            rebuild_league_snapshot(self.league)

        standings = {s.player_profile_id: s for s in LeagueStanding.objects.filter(league=self.league)}
        group_key = standings[self.profiles[0].id].unresolved_tie_group

        # Create resolution
        client = APIClient()
        admin_user = User.objects.create(username="admin_user", is_staff=True)
        regular_user = self.users[0]

        # Non-admin cannot list tie-resolutions
        client.force_authenticate(user=regular_user)
        res = client.get("/api/league/tie-resolutions/")
        self.assertEqual(res.status_code, 403)

        # Admin creates resolution
        client.force_authenticate(user=admin_user)
        res = client.post(
            f"/api/league/leagues/{self.league.id}/resolve-tie/",
            {
                "group_key": group_key,
                "reason": TieResolutionReason.WINNER_PERCENTAGE,
                "player_order": [self.profiles[0].id, self.profiles[1].id],
                "note": "Initial head to head",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 200)

        # Admin lists tie-resolutions
        res = client.get("/api/league/tie-resolutions/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        resolution_id = res.data[0]["id"]
        self.assertEqual(res.data[0]["group_key"], group_key)
        self.assertEqual(res.data[0]["reason"], TieResolutionReason.WINNER_PERCENTAGE)
        self.assertEqual(len(res.data[0]["entries"]), 2)
        self.assertEqual(res.data[0]["entries"][0]["player_profile_id"], self.profiles[0].id)
        self.assertIn("avatar_shape", res.data[0]["entries"][0])
        self.assertIn("avatar_color", res.data[0]["entries"][0])
        self.assertEqual(res.data[0]["entries"][1]["player_profile_id"], self.profiles[1].id)

        # Admin edits resolution: reverse player order and change reason
        with patch("services.standings_snapshot.compute_league_table", return_value=table):
            res = client.patch(
                f"/api/league/tie-resolutions/{resolution_id}/",
                {
                    "reason": TieResolutionReason.CANT_STOP,
                    "player_order": [self.profiles[1].id, self.profiles[0].id],
                    "note": "Correction: Cant stop played",
                },
                format="json",
            )
            self.assertEqual(res.status_code, 200)

        s0 = LeagueStanding.objects.get(league=self.league, player_profile=self.profiles[0])
        s1 = LeagueStanding.objects.get(league=self.league, player_profile=self.profiles[1])
        self.assertGreater(s1.tie_break_priority, s0.tie_break_priority)

        # Admin deletes resolution: tie group is restored and priorities reset
        with patch("services.standings_snapshot.compute_league_table", return_value=table):
            res = client.delete(f"/api/league/tie-resolutions/{resolution_id}/")
            self.assertEqual(res.status_code, 204)

        s0 = LeagueStanding.objects.get(league=self.league, player_profile=self.profiles[0])
        s1 = LeagueStanding.objects.get(league=self.league, player_profile=self.profiles[1])
        self.assertEqual(s0.tie_break_priority, 0)
        self.assertEqual(s1.tie_break_priority, 0)
        self.assertEqual(s0.unresolved_tie_group, group_key)
        self.assertEqual(s1.unresolved_tie_group, group_key)
