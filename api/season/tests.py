from django.test import TestCase
from rest_framework.test import APIClient

from season.queries import get_open_season
from user.models import User, PlayerProfile
from season.models import Season, SeasonParticipant
from season.services import (
    create_next_season,
    start_open_season,
    close_season,
    rank_participants,
    open_registration,
    apply_promotion,
)
from league.models import League, LeagueStanding, LeagueStatus
from game.models import Game, SelectedGame, BanDecision, Platform
from season_manager import start_new_season


class SeasonManagerTest(TestCase):
    def test_start_new_season_closes_running_season(self):
        # Create a running season
        running_season = Season.objects.create(
            year=2025, month=11, status=Season.SeasonStatus.RUNNING
        )
        # Create an open season
        open_season = Season.objects.create(
            year=2025, month=12, status=Season.SeasonStatus.OPEN
        )
        # Add some participants (at least 2 for _players_per_league to work without IndexError if I'm unlucky)
        p1 = PlayerProfile.objects.create(profile_name="P1")
        p2 = PlayerProfile.objects.create(profile_name="P2")
        SeasonParticipant.objects.create(season=open_season, profile=p1)
        SeasonParticipant.objects.create(season=open_season, profile=p2)

        start_new_season()

        running_season.refresh_from_db()
        open_season.refresh_from_db()

        self.assertEqual(running_season.status, Season.SeasonStatus.DONE)
        self.assertEqual(open_season.status, Season.SeasonStatus.RUNNING)

    def test_start_new_season_no_open_season(self):
        # Should now return early without error (graceful exit for auto-script)
        start_new_season()


class SeasonLogicTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username="admin", password="password")
        self.client.force_authenticate(user=self.user)

    def test_season_is_completed_requires_participants_and_results(self):
        # 1. Season with status DONE but no participants and no results -> False
        empty_done_season = Season.objects.create(
            year=2025, month=10, status=Season.SeasonStatus.DONE
        )
        self.assertFalse(empty_done_season.is_completed)

        # 2. Season with participants, but no results, status DONE -> False
        p1 = PlayerProfile.objects.create(profile_name="P1")
        sp1 = SeasonParticipant.objects.create(season=empty_done_season, profile=p1)
        self.assertFalse(empty_done_season.is_completed)

        # 3. Season with participants and results, status DONE -> True
        platform = Platform.objects.create(name="BGA_Test")
        game = Game.objects.create(name="Game1", platform=platform)
        league = League.objects.create(season=empty_done_season, level=1)
        league.members.add(sp1)
        sg = SelectedGame.objects.create(league=league, profile=p1, game=game)
        from result.models import Result
        Result.objects.create(
            season=empty_done_season,
            league=league,
            selected_game=sg,
            player_profile=p1,
            points=10,
            position=1,
        )
        self.assertTrue(empty_done_season.is_completed)

        # 4. Season with status DONE, participants and some results, but unfinished games -> False
        incomplete_done_season = Season.objects.create(
            year=2025, month=11, status=Season.SeasonStatus.DONE
        )
        p_a = PlayerProfile.objects.create(profile_name="P_A")
        p_b = PlayerProfile.objects.create(profile_name="P_B")
        sp_a = SeasonParticipant.objects.create(season=incomplete_done_season, profile=p_a)
        sp_b = SeasonParticipant.objects.create(season=incomplete_done_season, profile=p_b)
        league_2p = League.objects.create(season=incomplete_done_season, level=1)
        league_2p.members.add(sp_a, sp_b)
        sg_a = SelectedGame.objects.create(league=league_2p, profile=p_a, game=game)
        Result.objects.create(
            season=incomplete_done_season,
            league=league_2p,
            selected_game=sg_a,
            player_profile=p_a,
            points=10,
            position=1,
        )
        self.assertFalse(incomplete_done_season.is_completed)

    def test_season_lifecycle(self):
        # Create a running season
        season = Season.objects.create(
            year=2026, month=1, status=Season.SeasonStatus.RUNNING
        )

        # Close it
        close_season(season)
        season.refresh_from_db()
        self.assertEqual(season.status, Season.SeasonStatus.DONE)

        # Create next (NEXT)
        next_season = create_next_season(season)
        self.assertEqual(next_season.year, 2026)
        self.assertEqual(next_season.month, 2)
        self.assertEqual(next_season.status, Season.SeasonStatus.NEXT)

        # Open registration (OPEN)
        open_registration(next_season)
        self.assertEqual(next_season.status, Season.SeasonStatus.OPEN)

        # Open it (RUNNING)
        open_season = get_open_season()
        opened = start_open_season(open_season)
        self.assertEqual(opened.id, next_season.id)
        self.assertEqual(opened.status, Season.SeasonStatus.RUNNING)


class SeasonAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.profile = PlayerProfile.objects.create(
            user=self.user, profile_name="Test Profile"
        )
        self.client.force_authenticate(user=self.user)
        self.season = Season.objects.create(
            year=2026, month=1, status=Season.SeasonStatus.OPEN
        )

    def test_register_for_season(self):
        response = self.client.post("/api/season/register/")
        self.assertEqual(response.status_code, 200)  # Response is 200 with message
        self.assertTrue(
            SeasonParticipant.objects.filter(
                season=self.season, profile=self.profile
            ).exists()
        )

    def test_current_champion_none_when_no_done_season(self):
        response = self.client.get("/api/season/seasons/current-champion/")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data)

    def test_season_serializer_flags_for_empty_and_done_seasons(self):
        # 1. Empty DONE season: no participants, no results
        empty_season = Season.objects.create(
            year=2025, month=9, status=Season.SeasonStatus.DONE
        )
        resp = self.client.get(f"/api/season/seasons/{empty_season.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.data["is_completed"])
        self.assertTrue(resp.data["is_empty"])
        self.assertFalse(resp.data["is_incomplete"])

        # 2. Incomplete DONE season: participants exist, but no results
        incomplete_season = Season.objects.create(
            year=2025, month=8, status=Season.SeasonStatus.DONE
        )
        p = PlayerProfile.objects.create(profile_name="Participant_Only")
        SeasonParticipant.objects.create(season=incomplete_season, profile=p)
        resp = self.client.get(f"/api/season/seasons/{incomplete_season.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.data["is_completed"])
        self.assertFalse(resp.data["is_empty"])
        self.assertTrue(resp.data["is_incomplete"])

        # 3. Incomplete DONE season: participants and partial results exist
        partial_season = Season.objects.create(
            year=2025, month=7, status=Season.SeasonStatus.DONE
        )
        p_p1 = PlayerProfile.objects.create(profile_name="P_P1")
        p_p2 = PlayerProfile.objects.create(profile_name="P_P2")
        sp_p1 = SeasonParticipant.objects.create(season=partial_season, profile=p_p1)
        sp_p2 = SeasonParticipant.objects.create(season=partial_season, profile=p_p2)
        l_partial = League.objects.create(season=partial_season, level=1)
        l_partial.members.add(sp_p1, sp_p2)
        platform_p = Platform.objects.create(name="BGA_Part")
        game_p = Game.objects.create(name="GamePart", platform=platform_p)
        sg_part = SelectedGame.objects.create(league=l_partial, profile=p_p1, game=game_p)
        from result.models import Result
        Result.objects.create(
            season=partial_season,
            league=l_partial,
            selected_game=sg_part,
            player_profile=p_p1,
            points=10,
            position=1,
        )
        resp = self.client.get(f"/api/season/seasons/{partial_season.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.data["is_completed"])
        self.assertFalse(resp.data["is_empty"])
        self.assertTrue(resp.data["is_incomplete"])

    def test_season_participant_has_results_and_deletion(self):
        admin = User.objects.create_superuser(username="admin_p", password="pw")
        self.client.force_authenticate(user=admin)

        sp = SeasonParticipant.objects.create(
            season=self.season, profile=self.profile
        )
        league = League.objects.create(season=self.season, level=1)
        league.members.add(sp)

        # Before results
        resp = self.client.get(f"/api/season/season-participants/{sp.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.data["has_results"])

        from result.models import Result
        from game.models import SelectedGame, Game, Platform

        platform = Platform.objects.create(name="BGA_test")
        game = Game.objects.create(name="Game1", platform=platform)
        sg = SelectedGame.objects.create(
            league=league, profile=self.profile, game=game
        )
        res = Result.objects.create(
            season=self.season,
            league=league,
            selected_game=sg,
            player_profile=self.profile,
            points=10,
            position=1,
        )

        # After results
        resp = self.client.get(f"/api/season/season-participants/{sp.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data["has_results"])

        # Try deleting participant with results -> 400
        del_resp = self.client.delete(f"/api/season/season-participants/{sp.id}/")
        self.assertEqual(del_resp.status_code, 400)
        self.assertIn("results already exist", del_resp.data["detail"])
        self.assertTrue(SeasonParticipant.objects.filter(id=sp.id).exists())

        # Try fill-leagues on season with results -> 400
        fill_resp = self.client.post(f"/api/season/seasons/{self.season.id}/fill-leagues/")
        self.assertEqual(fill_resp.status_code, 400)
        self.assertIn("results already exist", fill_resp.data["detail"])

        # Remove result and delete participant -> 204
        res.delete()
        del_resp = self.client.delete(f"/api/season/season-participants/{sp.id}/")
        self.assertEqual(del_resp.status_code, 204)
        self.assertFalse(SeasonParticipant.objects.filter(id=sp.id).exists())

    def test_current_champion_returns_latest_done_season_winner(self):
        s1 = Season.objects.create(
            year=2025, month=11, status=Season.SeasonStatus.DONE
        )
        s2 = Season.objects.create(
            year=2025, month=12, status=Season.SeasonStatus.DONE
        )
        # S1 winner
        l1 = League.objects.create(season=s1, level=1)
        p1 = PlayerProfile.objects.create(profile_name="P1")
        LeagueStanding.objects.create(league=l1, player_profile=p1, league_points=10)

        # S2 winner (level 1)
        l2_1 = League.objects.create(season=s2, level=1)
        champ_user = User.objects.create_user(username="champ", password="password")
        p2 = PlayerProfile.objects.create(user=champ_user, profile_name="Champ Profile")
        p3 = PlayerProfile.objects.create(profile_name="Runner Up")
        LeagueStanding.objects.create(league=l2_1, player_profile=p2, league_points=25)
        LeagueStanding.objects.create(league=l2_1, player_profile=p3, league_points=20)

        # S2 level 2 winner (should NOT be crowned overall champion)
        l2_2 = League.objects.create(season=s2, level=2)
        p4 = PlayerProfile.objects.create(profile_name="Lvl2 Winner")
        LeagueStanding.objects.create(league=l2_2, player_profile=p4, league_points=30)

        # Query endpoint
        response = self.client.get("/api/season/seasons/current-champion/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "champ")
        self.assertEqual(response.data["season_id"], s2.id)
        self.assertEqual(response.data["profile_id"], p2.id)
        self.assertEqual(response.data["league_points"], 25)

    def test_league_winners_empty_when_season_not_completed(self):
        s_running = Season.objects.create(
            year=2026, month=5, status=Season.SeasonStatus.RUNNING
        )
        l1 = League.objects.create(season=s_running, level=1)
        p1 = PlayerProfile.objects.create(profile_name="Leader")
        LeagueStanding.objects.create(league=l1, player_profile=p1, league_points=30)

        response = self.client.get(f"/api/season/seasons/{s_running.id}/league-winners/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["winners"], [])

    def test_league_winners_returned_when_season_done(self):
        s_done = Season.objects.create(
            year=2026, month=4, status=Season.SeasonStatus.DONE
        )
        l1 = League.objects.create(season=s_done, level=1)
        user = User.objects.create_user(
            username="winner_user",
            password="password",
            avatar_shape="star",
            avatar_color="#dc2626",
        )
        p1 = PlayerProfile.objects.create(user=user, profile_name="Winner Profile")
        sp1 = SeasonParticipant.objects.create(season=s_done, profile=p1)
        l1.members.add(sp1)
        platform = Platform.objects.create(name="BGA_Winner_Test")
        game = Game.objects.create(name="GameW", platform=platform)
        sg = SelectedGame.objects.create(league=l1, profile=p1, game=game)
        from result.models import Result
        Result.objects.create(
            season=s_done,
            league=l1,
            selected_game=sg,
            player_profile=p1,
            points=30,
            position=1,
        )
        LeagueStanding.objects.create(league=l1, player_profile=p1, league_points=30)

        response = self.client.get(f"/api/season/seasons/{s_done.id}/league-winners/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["winners"]), 1)
        self.assertEqual(response.data["winners"][0]["winner"]["username"], "winner_user")
        self.assertEqual(response.data["winners"][0]["winner"]["avatar_shape"], "star")
        self.assertEqual(response.data["winners"][0]["winner"]["avatar_color"], "#dc2626")

    def test_leaderboard_custom_avatar(self):
        s_done = Season.objects.create(
            year=2026, month=4, status=Season.SeasonStatus.DONE
        )
        l1 = League.objects.create(season=s_done, level=1, status=LeagueStatus.DONE)
        user = User.objects.create_user(
            username="hall_hero",
            password="password",
            avatar_shape="crown",
            avatar_color="#eab308",
        )
        p1 = PlayerProfile.objects.create(user=user, profile_name="Hall Hero")
        LeagueStanding.objects.create(league=l1, player_profile=p1, league_points=30)

        response = self.client.get("/api/leaderboard/?year=2026")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["standings"]), 1)
        standing = response.data["standings"][0]
        self.assertEqual(standing["username"], "hall_hero")
        self.assertEqual(standing["avatar_shape"], "crown")
        self.assertEqual(standing["avatar_color"], "#eab308")

    def test_leaderboard_all_time(self):
        s1 = Season.objects.create(year=2025, month=4, status=Season.SeasonStatus.DONE)
        s2 = Season.objects.create(year=2026, month=4, status=Season.SeasonStatus.DONE)
        l1 = League.objects.create(season=s1, level=1, status=LeagueStatus.DONE)
        l2 = League.objects.create(season=s2, level=1, status=LeagueStatus.DONE)

        p1 = PlayerProfile.objects.create(profile_name="P1")
        p2 = PlayerProfile.objects.create(profile_name="P2")

        LeagueStanding.objects.create(league=l1, player_profile=p1, league_points=30)
        LeagueStanding.objects.create(league=l1, player_profile=p2, league_points=20)
        LeagueStanding.objects.create(league=l2, player_profile=p1, league_points=30)

        # year=all query param
        response_all = self.client.get("/api/leaderboard/?year=all")
        self.assertEqual(response_all.status_code, 200)
        self.assertEqual(response_all.data["year"], "all")
        self.assertEqual(len(response_all.data["standings"]), 2)
        p1_stats = next(s for s in response_all.data["standings"] if s["player_profile_id"] == p1.id)
        # P1 came 1st in both leagues
        self.assertEqual(p1_stats["per_level"]["1"]["first"], 2)

        # omitted year query param
        response_none = self.client.get("/api/leaderboard/")
        self.assertEqual(response_none.status_code, 200)
        self.assertEqual(response_none.data["year"], "all")
        self.assertEqual(len(response_none.data["standings"]), 2)

    def test_admin_can_add_and_remove_participant(self):
        admin = User.objects.create_superuser(username="superadmin", password="password")
        self.client.force_authenticate(user=admin)
        new_profile = PlayerProfile.objects.create(profile_name="New Participant")

        # Admin adds participant
        res = self.client.post(
            "/api/season/season-participants/",
            {"season": self.season.id, "profile": new_profile.id},
        )
        self.assertEqual(res.status_code, 201)
        participant_id = res.data["id"]
        self.assertTrue(
            SeasonParticipant.objects.filter(id=participant_id, season=self.season, profile=new_profile).exists()
        )

        # Duplicate addition is rejected
        res_dup = self.client.post(
            "/api/season/season-participants/",
            {"season": self.season.id, "profile": new_profile.id},
        )
        self.assertEqual(res_dup.status_code, 400)

        # Admin deletes participant
        res_del = self.client.delete(f"/api/season/season-participants/{participant_id}/")
        self.assertEqual(res_del.status_code, 204)
        self.assertFalse(
            SeasonParticipant.objects.filter(id=participant_id).exists()
        )

    def test_non_admin_cannot_add_or_remove_participant(self):
        # Authenticated non-admin
        new_profile = PlayerProfile.objects.create(profile_name="Other Profile")
        res_add = self.client.post(
            "/api/season/season-participants/",
            {"season": self.season.id, "profile": new_profile.id},
        )
        self.assertEqual(res_add.status_code, 403)

        sp = SeasonParticipant.objects.create(season=self.season, profile=new_profile)
        res_del = self.client.delete(f"/api/season/season-participants/{sp.id}/")
        self.assertEqual(res_del.status_code, 403)


class ProjectedLeaguesAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username="admin", password="password"
        )
        self.client.force_authenticate(user=self.admin)
        self.s1 = Season.objects.create(
            year=2026, month=1, status=Season.SeasonStatus.DONE
        )
        self.s2 = Season.objects.create(
            year=2026, month=2, status=Season.SeasonStatus.OPEN
        )
        self.p1 = PlayerProfile.objects.create(profile_name="P1")
        self.p2 = PlayerProfile.objects.create(profile_name="P2")
        self.p3 = PlayerProfile.objects.create(profile_name="P3")

        # P1 & P2 were in season 1
        SeasonParticipant.objects.create(season=self.s1, profile=self.p1)
        SeasonParticipant.objects.create(season=self.s1, profile=self.p2)

        # Only P1 & P3 registered for season 2 (P2 is missing, P3 is newcomer)
        SeasonParticipant.objects.create(season=self.s2, profile=self.p1)
        SeasonParticipant.objects.create(season=self.s2, profile=self.p3)

    def test_projected_leagues_returns_partitioned_participants(self):
        response = self.client.get(
            f"/api/season/season-participants/projected-leagues/?season={self.s2.id}"
        )
        self.assertEqual(response.status_code, 200)
        data = response.data

        self.assertEqual(data["season"]["id"], self.s2.id)

        # Active participants: P1 and P3
        active_ids = [p["profile"] for p in data["active_participants"]]
        self.assertEqual(set(active_ids), {self.p1.id, self.p3.id})

        # Missing participants: P2
        missing_ids = [p["profile"] for p in data["missing_participants"]]
        self.assertEqual(missing_ids, [self.p2.id])

        # Newcomers: P3
        newcomer_ids = [p["profile"] for p in data["newcomers"]]
        self.assertIn(self.p3.id, newcomer_ids)

        # Unprojected: empty (all are accounted for in leagues or newcomers)
        self.assertEqual(data["unprojected_participants"], [])


class PreviewLeaguesAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username="admin", password="password"
        )
        self.client.force_authenticate(user=self.admin)
        self.p1 = PlayerProfile.objects.create(profile_name="P1")
        self.p2 = PlayerProfile.objects.create(profile_name="P2")

    def test_preview_leagues_returns_distribution_without_persisting(self):
        response = self.client.post(
            "/api/season/season-participants/preview-leagues/",
            {"profile_ids": [self.p1.id, self.p2.id]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        leagues = response.data["leagues"]
        self.assertEqual(len(leagues), 1)
        all_members = leagues[0]["members"] + response.data["newcomers"]
        self.assertEqual(len(all_members), 2)

        # Nothing should have been persisted.
        self.assertEqual(Season.objects.count(), 0)
        self.assertEqual(League.objects.count(), 0)
        self.assertEqual(SeasonParticipant.objects.count(), 0)

    def test_preview_leagues_empty_profile_ids(self):
        response = self.client.post(
            "/api/season/season-participants/preview-leagues/",
            {"profile_ids": []},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["leagues"], [])
        self.assertEqual(response.data["newcomers"], [])

    def test_preview_leagues_rejects_non_integer_ids(self):
        response = self.client.post(
            "/api/season/season-participants/preview-leagues/",
            {"profile_ids": ["abc"]},
            format="json",
        )
        self.assertEqual(response.status_code, 400)


class FillLeaguesAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username="admin", password="password"
        )
        self.client.force_authenticate(user=self.admin)
        self.season = Season.objects.create(
            year=2026, month=2, status=Season.SeasonStatus.OPEN
        )
        self.p1 = PlayerProfile.objects.create(profile_name="P1")
        self.p2 = PlayerProfile.objects.create(profile_name="P2")
        SeasonParticipant.objects.create(season=self.season, profile=self.p1)
        SeasonParticipant.objects.create(season=self.season, profile=self.p2)

    def test_fill_leagues_creates_leagues_from_participants(self):
        response = self.client.post(
            f"/api/season/seasons/{self.season.id}/fill-leagues/"
        )
        self.assertEqual(response.status_code, 200)
        leagues = League.objects.filter(season=self.season)
        self.assertEqual(leagues.count(), 1)
        self.assertEqual(leagues.first().members.count(), 2)

    def test_fill_leagues_replaces_existing_leagues(self):
        # Pre-existing (stale) league for the season.
        League.objects.create(season=self.season, level=1)
        response = self.client.post(
            f"/api/season/seasons/{self.season.id}/fill-leagues/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(League.objects.filter(season=self.season).count(), 1)

    def test_fill_leagues_rejects_non_open_season(self):
        running_season = Season.objects.create(
            year=2026, month=3, status=Season.SeasonStatus.RUNNING
        )
        response = self.client.post(
            f"/api/season/seasons/{running_season.id}/fill-leagues/"
        )
        self.assertEqual(response.status_code, 400)

    def test_fill_leagues_rejects_when_no_participants(self):
        empty_season = Season.objects.create(
            year=2026, month=4, status=Season.SeasonStatus.OPEN
        )
        response = self.client.post(
            f"/api/season/seasons/{empty_season.id}/fill-leagues/"
        )
        self.assertEqual(response.status_code, 400)


class RankParticipantsTest(TestCase):
    def setUp(self):
        # Setup previous season
        self.prev_season = Season.objects.create(
            year=2025, month=12, status=Season.SeasonStatus.DONE
        )

        # 4 players in L1
        self.p1 = PlayerProfile.objects.create(profile_name="P1")
        self.p2 = PlayerProfile.objects.create(profile_name="P2")
        self.p3 = PlayerProfile.objects.create(profile_name="P3")
        self.p4 = PlayerProfile.objects.create(profile_name="P4")

        # 4 players in L2
        self.p5 = PlayerProfile.objects.create(profile_name="P5")
        self.p6 = PlayerProfile.objects.create(profile_name="P6")
        self.p7 = PlayerProfile.objects.create(profile_name="P7")
        self.p8 = PlayerProfile.objects.create(profile_name="P8")

        # Previous season participants
        self.prev_participants = {}
        for p in [
            self.p1,
            self.p2,
            self.p3,
            self.p4,
            self.p5,
            self.p6,
            self.p7,
            self.p8,
        ]:
            self.prev_participants[p.profile_name] = SeasonParticipant.objects.create(
                season=self.prev_season, profile=p
            )

        self.l1 = League.objects.create(season=self.prev_season, level=1)
        self.l2 = League.objects.create(season=self.prev_season, level=2)

        # Add participants to leagues
        for p_name in ["P1", "P2", "P3", "P4"]:
            self.l1.members.add(self.prev_participants[p_name])
        for p_name in ["P5", "P6", "P7", "P8"]:
            self.l2.members.add(self.prev_participants[p_name])

        # L1 standings
        LeagueStanding.objects.create(
            league=self.l1, player_profile=self.p1, league_points=10
        )
        LeagueStanding.objects.create(
            league=self.l1, player_profile=self.p2, league_points=8
        )
        LeagueStanding.objects.create(
            league=self.l1, player_profile=self.p3, league_points=6
        )
        LeagueStanding.objects.create(
            league=self.l1, player_profile=self.p4, league_points=4
        )  # Last in L1

        # L2 standings
        LeagueStanding.objects.create(
            league=self.l2, player_profile=self.p5, league_points=10
        )  # Winner L2
        LeagueStanding.objects.create(
            league=self.l2, player_profile=self.p6, league_points=8
        )
        LeagueStanding.objects.create(
            league=self.l2, player_profile=self.p7, league_points=6
        )
        LeagueStanding.objects.create(
            league=self.l2, player_profile=self.p8, league_points=4
        )

        # New season
        self.new_season = Season.objects.create(
            year=2026, month=1, status=Season.SeasonStatus.OPEN
        )

        # Participants for new season: all old ones + some new ones
        self.new_p1 = PlayerProfile.objects.create(profile_name="New1")
        self.new_p2 = PlayerProfile.objects.create(profile_name="New2")

        self.all_profiles = [
            self.p1,
            self.p2,
            self.p3,
            self.p4,
            self.p5,
            self.p6,
            self.p7,
            self.p8,
            self.new_p1,
            self.new_p2,
        ]
        self.participants = []
        for p in self.all_profiles:
            self.participants.append(
                SeasonParticipant.objects.create(season=self.new_season, profile=p)
            )

    def test_rank_participants_order(self):
        ranked = rank_participants(self.new_season, self.participants)

        # Check that we got all back
        self.assertEqual(len(ranked), 10)

        # Ranks should be 1 to 10
        self.assertEqual([p.rank for p in ranked], list(range(1, 11)))

        # Check order:
        # P1, P2, P3 are L1 top 3. P4 is last in L1. P5 is winner of L2.
        # apply_promotion should swap P4 and P5.
        # Expected order: P1, P2, P3, P5, P4, P6, P7, P8, (New1, New2 in any order)

        ranked_profiles = [p.profile for p in ranked]
        self.assertEqual(ranked_profiles[0], self.p1)
        self.assertEqual(ranked_profiles[1], self.p2)
        self.assertEqual(ranked_profiles[2], self.p3)
        self.assertEqual(ranked_profiles[3], self.p5)  # Promoted
        self.assertEqual(ranked_profiles[4], self.p4)  # Relegated
        self.assertEqual(ranked_profiles[5], self.p6)
        self.assertEqual(ranked_profiles[6], self.p7)
        self.assertEqual(ranked_profiles[7], self.p8)

        # New players should be at the end
        self.assertIn(ranked_profiles[8], [self.new_p1, self.new_p2])
        self.assertIn(ranked_profiles[9], [self.new_p1, self.new_p2])


def _row(name, league, position, is_last=False):
    return {
        "profile": name,
        "league": league,
        "position": position,
        "is_last": is_last,
    }


class ApplyPromotionRulesTest(TestCase):
    """Pure logic tests for apply_promotion covering the
    promotion-guaranteed and last-forces-relegation rules.
    """

    def test_classic_swap_when_full_league_sizes_match(self):
        # 8 players, sizes [4, 4]. Last of L1 swaps with winner of L2.
        rows = [
            _row("A", 1, 1),
            _row("B", 1, 2),
            _row("C", 1, 3),
            _row("D", 1, 4, is_last=True),
            _row("E", 2, 1),
            _row("F", 2, 2),
            _row("G", 2, 3),
            _row("H", 2, 4, is_last=True),
        ]
        result = [r["profile"] for r in apply_promotion(rows, [4, 4])]
        self.assertEqual(result, ["A", "B", "C", "E", "D", "F", "G", "H"])

    def test_third_of_higher_league_relegated_to_keep_promotion(self):
        # New L1 shrinks to 3, L2 to 2. Winner of L2 must still be promoted
        # even though L1 is "full" without him; the 3rd of L1 is relegated.
        # Last of L1 (D) did not register.
        rows = [
            _row("A", 1, 1),
            _row("B", 1, 2),
            _row("C", 1, 3),
            _row("E", 2, 1),
            _row("F", 2, 2, is_last=True),
        ]
        result = [r["profile"] for r in apply_promotion(rows, [3, 2])]
        # A, B keep L1; E promoted into L1; C relegated to L2; F stays last.
        self.assertEqual(result[:3], ["A", "B", "E"])
        self.assertEqual(set(result[3:]), {"C", "F"})
        # F was last in L2 -> should land in the bottom-most spot.
        self.assertEqual(result[-1], "F")

    def test_last_forces_relegation_pulling_extra_promotion_from_below(self):
        # Two L1 players did not register (A, B). D was last of L1 and
        # must still be relegated; F and G get promoted from L2 to fill L1.
        rows = [
            _row("C", 1, 3),
            _row("D", 1, 4, is_last=True),
            _row("E", 2, 1),
            _row("F", 2, 2),
            _row("G", 2, 3),
            _row("H", 2, 4, is_last=True),
        ]
        result = [r["profile"] for r in apply_promotion(rows, [4, 2])]
        # New L1 = [C, E, F, G]; D forced down to L2 with H.
        self.assertEqual(result[:4], ["C", "E", "F", "G"])
        self.assertEqual(set(result[4:]), {"D", "H"})

    def test_collapsed_pyramid_promotion_outranks_relegation(self):
        # Previous 5 leagues x 4 players. All of L2, L3, L4 skip
        # registration. L1 and L5 register fully -> 8 players, new
        # structure [4, 4]. The winner of L5 (Q) must be promoted into
        # new L1, and the last of L1 (D) must be relegated to new L2.
        rows = [
            _row("A", 1, 1),
            _row("B", 1, 2),
            _row("C", 1, 3),
            _row("D", 1, 4, is_last=True),
            _row("Q", 5, 1),
            _row("R", 5, 2),
            _row("S", 5, 3),
            _row("T", 5, 4, is_last=True),
        ]
        result = [r["profile"] for r in apply_promotion(rows, [4, 4])]
        self.assertEqual(set(result[:4]), {"A", "B", "C", "Q"})
        self.assertEqual(set(result[4:]), {"D", "R", "S", "T"})
        # Q (promoted winner) must end up above D (relegated last).
        self.assertLess(result.index("Q"), result.index("D"))

    def test_no_violation_when_winner_already_in_higher_league(self):
        # Standard case with new players: previous registered players
        # already line up correctly, no swap needed.
        rows = [
            _row("A", 1, 1),
            _row("B", 1, 2),
            _row("C", 1, 3),
            _row("D", 1, 4, is_last=True),
            _row("E", 2, 1),
            _row("F", 2, 2),
        ]
        result = [r["profile"] for r in apply_promotion(rows, [4, 4])]
        # E promoted above D (the last), D relegated.
        self.assertEqual(result, ["A", "B", "C", "E", "D", "F"])


class LiveEventsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.force_authenticate(user=self.user)
        self.season = Season.objects.create(
            year=2026, month=3, status=Season.SeasonStatus.RUNNING
        )
        self.p1 = PlayerProfile.objects.create(profile_name="Player 1")
        self.p2 = PlayerProfile.objects.create(profile_name="Player 2")
        self.p3 = PlayerProfile.objects.create(profile_name="Player 3")

        self.sp1 = SeasonParticipant.objects.create(
            season=self.season, profile=self.p1
        )
        self.sp2 = SeasonParticipant.objects.create(
            season=self.season, profile=self.p2
        )
        self.sp3 = SeasonParticipant.objects.create(
            season=self.season, profile=self.p3
        )

        self.league1 = League.objects.create(season=self.season, level=1)
        self.league1.members.add(self.sp1, self.sp2)

        self.league2 = League.objects.create(season=self.season, level=2)
        self.league2.members.add(self.sp3)

        self.platform = Platform.objects.create(name="BGA")
        self.game1 = Game.objects.create(name="Terraforming Mars", platform=self.platform)
        self.game2 = Game.objects.create(name="Ark Nova", platform=self.platform)

        self.pick1 = SelectedGame.objects.create(
            league=self.league1, profile=self.p1, game=self.game1
        )
        self.pick2 = SelectedGame.objects.create(
            league=self.league2, profile=self.p3, game=self.game2
        )
        self.ban1 = BanDecision.objects.create(
            league=self.league1, player_banning=self.p2, skipped_ban=True
        )

    def test_live_events_returns_all_for_season(self):
        response = self.client.get(
            f"/api/season/live-events/?season_id={self.season.id}"
        )
        self.assertEqual(response.status_code, 200)
        event_types = [e["type"] for e in response.data]
        self.assertIn("PICK", event_types)
        self.assertIn("BAN", event_types)
        self.assertEqual(len(response.data), 3)

    def test_live_events_filter_by_league_id(self):
        response = self.client.get(
            f"/api/season/live-events/?league_id={self.league1.id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        for event in response.data:
            self.assertEqual(event["leagueId"], self.league1.id)

        # Check skip ban event is included in league 1
        ban_events = [e for e in response.data if e["type"] == "BAN"]
        self.assertEqual(len(ban_events), 1)
        self.assertTrue(ban_events[0]["data"]["skippedBan"])
        self.assertEqual(ban_events[0]["data"]["playerName"], "Player 2")


class OpenRegistrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username="adminuser", password="password"
        )
        self.regular_user = User.objects.create_user(
            username="regularuser", password="password"
        )

    def test_admin_can_open_next_season(self):
        season = Season.objects.create(
            year=2026, month=5, status=Season.SeasonStatus.NEXT
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            f"/api/season/seasons/{season.id}/open-registration/"
        )
        self.assertEqual(response.status_code, 200)
        season.refresh_from_db()
        self.assertEqual(season.status, Season.SeasonStatus.OPEN)

    def test_cannot_open_running_or_done_season(self):
        season = Season.objects.create(
            year=2026, month=5, status=Season.SeasonStatus.RUNNING
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            f"/api/season/seasons/{season.id}/open-registration/"
        )
        self.assertEqual(response.status_code, 400)

    def test_regular_user_cannot_open_season(self):
        season = Season.objects.create(
            year=2026, month=5, status=Season.SeasonStatus.NEXT
        )
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(
            f"/api/season/seasons/{season.id}/open-registration/"
        )
        self.assertEqual(response.status_code, 403)

    def test_open_next_season_management_command(self):
        from django.core.management import call_command
        from io import StringIO

        season = Season.objects.create(
            year=2026, month=6, status=Season.SeasonStatus.NEXT
        )
        out = StringIO()
        call_command("open_next_season", stdout=out)
        season.refresh_from_db()
        self.assertEqual(season.status, Season.SeasonStatus.OPEN)
        self.assertIn("open for registration", out.getvalue())

    def test_open_next_season_does_nothing_when_no_next_season(self):
        from season_manager import open_next_season
        from django.core.management import call_command
        from io import StringIO

        # Only a running season exists, no NEXT season
        running_season = Season.objects.create(
            year=2026, month=5, status=Season.SeasonStatus.RUNNING
        )
        initial_count = Season.objects.count()

        result = open_next_season()
        self.assertIsNone(result)
        self.assertEqual(Season.objects.count(), initial_count)
        running_season.refresh_from_db()
        self.assertEqual(running_season.status, Season.SeasonStatus.RUNNING)

        # Also test management command does not fail and warns
        out = StringIO()
        call_command("open_next_season", stdout=out)
        self.assertIn("No season in NEXT status found", out.getvalue())
        self.assertEqual(Season.objects.count(), initial_count)

    def test_open_next_season_check_7_days_skips_when_not_seven_days_before(self):
        from django.core.management import call_command
        from io import StringIO
        from unittest.mock import patch
        from datetime import datetime, timezone as dt_timezone

        season = Season.objects.create(
            year=2026, month=6, status=Season.SeasonStatus.NEXT
        )
        out = StringIO()
        # Mock date to mid-month (e.g. 15th of 30-day or 31-day month)
        mock_now = datetime(2026, 5, 15, 12, 0, 0, tzinfo=dt_timezone.utc)
        with patch("django.utils.timezone.now", return_value=mock_now):
            call_command("open_next_season", check_7_days=True, stdout=out)

        season.refresh_from_db()
        self.assertEqual(season.status, Season.SeasonStatus.NEXT)
        self.assertIn("is not 7 days before the end of the month", out.getvalue())


class CronSeasonJobTests(TestCase):
    def test_cron_season_job_opens_season_seven_days_before_31_day_month(self):
        from django.core.management import call_command
        from io import StringIO

        season = Season.objects.create(
            year=2026, month=6, status=Season.SeasonStatus.NEXT
        )
        out = StringIO()
        # May has 31 days. 7 days before June 1 is May 25.
        call_command("cron_season_job", date="2026-05-25", stdout=out)
        season.refresh_from_db()
        self.assertEqual(season.status, Season.SeasonStatus.OPEN)
        self.assertIn("7 days before the new month", out.getvalue())
        self.assertIn("Running open_next_season", out.getvalue())

    def test_cron_season_job_opens_season_seven_days_before_30_day_month(self):
        from django.core.management import call_command
        from io import StringIO

        season = Season.objects.create(
            year=2026, month=5, status=Season.SeasonStatus.NEXT
        )
        out = StringIO()
        # April has 30 days. 7 days before May 1 is April 24.
        call_command("cron_season_job", date="2026-04-24", stdout=out)
        season.refresh_from_db()
        self.assertEqual(season.status, Season.SeasonStatus.OPEN)
        self.assertIn("7 days before the new month", out.getvalue())

    def test_cron_season_job_starts_season_on_first_day_of_month(self):
        from django.core.management import call_command
        from io import StringIO

        open_season = Season.objects.create(
            year=2026, month=6, status=Season.SeasonStatus.OPEN
        )
        out = StringIO()
        call_command("cron_season_job", date="2026-06-01", stdout=out)
        open_season.refresh_from_db()
        self.assertEqual(open_season.status, Season.SeasonStatus.RUNNING)
        self.assertIn("1st day of the month", out.getvalue())
        self.assertIn("Running start_new_season", out.getvalue())

    def test_cron_season_job_does_nothing_on_regular_day(self):
        from django.core.management import call_command
        from io import StringIO

        next_season = Season.objects.create(
            year=2026, month=6, status=Season.SeasonStatus.NEXT
        )
        out = StringIO()
        call_command("cron_season_job", date="2026-05-15", stdout=out)
        next_season.refresh_from_db()
        self.assertEqual(next_season.status, Season.SeasonStatus.NEXT)
        self.assertIn("No action required", out.getvalue())

    def test_cron_season_job_evaluates_berlin_timezone(self):
        from django.core.management import call_command
        from io import StringIO
        from unittest.mock import patch
        from datetime import datetime, timezone as dt_timezone

        next_season = Season.objects.create(
            year=2026, month=6, status=Season.SeasonStatus.NEXT
        )
        out = StringIO()
        # At 22:30 UTC on May 24th, Berlin (UTC+2 in DST) is 00:30 on May 25th (7 days before June 1st)
        mock_now = datetime(2026, 5, 24, 22, 30, 0, tzinfo=dt_timezone.utc)
        with patch("season.management.commands.cron_season_job.datetime") as mock_dt:
            mock_dt.now.return_value = mock_now
            mock_dt.strptime = datetime.strptime
            call_command("cron_season_job", stdout=out)

        next_season.refresh_from_db()
        self.assertEqual(next_season.status, Season.SeasonStatus.OPEN)
        self.assertIn("2026-05-25", out.getvalue())


class SeasonProgressTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username="admin_prog", password="password")
        self.client.force_authenticate(user=self.user)

    def test_season_progress_empty_and_done(self):
        from season.queries import get_season_progress

        # Empty season with no leagues
        empty_season = Season.objects.create(
            year=2026, month=7, status=Season.SeasonStatus.RUNNING
        )
        prog = get_season_progress(empty_season)
        self.assertEqual(prog["percentage"], 0.0)
        self.assertEqual(prog["picks"]["total"], 0)
        self.assertEqual(prog["reports"]["total"], 0)

        # Done season
        done_season = Season.objects.create(
            year=2026, month=8, status=Season.SeasonStatus.DONE
        )
        prog_done = get_season_progress(done_season)
        self.assertEqual(prog_done["percentage"], 100.0)

    def test_season_progress_weighting_calculation(self):
        from season.queries import get_season_progress
        from result.models import Result

        season = Season.objects.create(
            year=2026, month=9, status=Season.SeasonStatus.RUNNING
        )
        p1 = PlayerProfile.objects.create(profile_name="Prog_P1")
        p2 = PlayerProfile.objects.create(profile_name="Prog_P2")
        sp1 = SeasonParticipant.objects.create(season=season, profile=p1, rank=1)
        sp2 = SeasonParticipant.objects.create(season=season, profile=p2, rank=2)

        league = League.objects.create(season=season, level=1, status=LeagueStatus.PICKING)
        league.members.add(sp1, sp2)

        platform = Platform.objects.create(name="BGA_Prog")
        g1 = Game.objects.create(name="Game Prog 1", platform=platform)
        g2 = Game.objects.create(name="Game Prog 2", platform=platform)
        g3 = Game.objects.create(name="Game Prog 3", platform=platform)
        g4 = Game.objects.create(name="Game Prog 4", platform=platform)

        # 1. Initially 0 picks done
        prog = get_season_progress(season)
        self.assertEqual(prog["percentage"], 0.0)
        self.assertEqual(prog["picks"]["total"], 4)
        self.assertEqual(prog["bans"]["total"], 2)
        self.assertEqual(prog["reports"]["total"], 4)

        # 2. Add all 4 picks (picks complete -> 7.5%)
        sg1 = SelectedGame.objects.create(league=league, profile=p1, game=g1)
        sg2 = SelectedGame.objects.create(league=league, profile=p1, game=g2)
        sg3 = SelectedGame.objects.create(league=league, profile=p2, game=g3)
        sg4 = SelectedGame.objects.create(league=league, profile=p2, game=g4)

        prog = get_season_progress(season)
        self.assertEqual(prog["picks"]["current"], 4)
        self.assertEqual(prog["picks"]["missing"], 0)
        self.assertEqual(prog["percentage"], 7.5)

        # 3. Add all 2 bans (bans complete -> 2 games banned, which flags 2 repicks needed)
        BanDecision.objects.create(league=league, player_banning=p1, selected_game=sg3)
        BanDecision.objects.create(league=league, player_banning=p2, selected_game=sg1)

        prog = get_season_progress(season)
        self.assertEqual(prog["bans"]["current"], 2)
        self.assertEqual(prog["bans"]["missing"], 0)
        # Because 2 games were banned, repicks are needed (picks_total becomes 6, current is 4)
        self.assertEqual(prog["picks"]["total"], 6)
        self.assertEqual(prog["percentage"], 12.5)

        # Repicks performed -> picks back to 100% -> 15.0%
        g5 = Game.objects.create(name="Game Prog 5", platform=platform)
        g6 = Game.objects.create(name="Game Prog 6", platform=platform)
        sg5 = SelectedGame.objects.create(league=league, profile=p1, game=g5)
        sg6 = SelectedGame.objects.create(league=league, profile=p2, game=g6)

        prog = get_season_progress(season)
        self.assertEqual(prog["picks"]["current"], 6)
        self.assertEqual(prog["picks"]["total"], 6)
        self.assertEqual(prog["percentage"], 15.0)

        # 4. Report 1 game out of 4 (playable games are sg2, sg4, sg5, sg6; each needs 2 results)
        # 1 complete game adds 85% * (1/4) = 21.25%, total reaches 36.2% or 36.3%
        Result.objects.create(
            season=season, league=league, selected_game=sg2, player_profile=p1, points=10, position=1
        )
        Result.objects.create(
            season=season, league=league, selected_game=sg2, player_profile=p2, points=5, position=2
        )

        prog = get_season_progress(season)
        self.assertEqual(prog["reports"]["current"], 1)
        self.assertEqual(prog["reports"]["missing"], 3)
        self.assertEqual(prog["percentage"], 36.2)

        # 5. Report remaining games
        for sg in [sg4, sg5, sg6]:
            Result.objects.create(
                season=season, league=league, selected_game=sg, player_profile=p1, points=8, position=2
            )
            Result.objects.create(
                season=season, league=league, selected_game=sg, player_profile=p2, points=12, position=1
            )
        prog = get_season_progress(season)
        # All playable games reported -> 100%
        self.assertEqual(prog["percentage"], 100.0)

    def test_season_progress_in_api_responses(self):
        season = Season.objects.create(
            year=2026, month=10, status=Season.SeasonStatus.RUNNING
        )
        # Current endpoint
        res = self.client.get("/api/season/current/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("progress", res.data)
        self.assertEqual(res.data["progress"]["percentage"], 0.0)

        # List endpoint
        res_list = self.client.get(f"/api/season/seasons/?year={season.year}")
        self.assertEqual(res_list.status_code, 200)
        item = next(s for s in res_list.data if s["id"] == season.id)
        self.assertIn("progress", item)

        # Full standings endpoint
        res_fs = self.client.get(f"/api/season/seasons/{season.id}/full-standings/")
        self.assertEqual(res_fs.status_code, 200)
        self.assertIn("progress", res_fs.data["season"])
