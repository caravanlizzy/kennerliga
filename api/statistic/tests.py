from decimal import Decimal

from django.test import TestCase

from game.models import Game, SelectedGame
from league.models import League, LeagueStanding
from result.models import Result
from season.models import Season
from statistic.services import (
    CATEGORY_DEFS,
    _build_player_pool,
    _rank_career,
    get_statistics_overview,
)
from user.models import PlayerProfile, Platform, User


class StatisticsServiceTestBase(TestCase):
    def setUp(self):
        self.season = Season.objects.create(
            year=2026, month=1, status=Season.SeasonStatus.RUNNING
        )
        self.platform = Platform.objects.create(name="BGA")

    def make_profile(self, name):
        user = User.objects.create_user(username=name, password="x")
        return PlayerProfile.objects.create(user=user, profile_name=name)

    def make_league(self, level):
        return League.objects.create(season=self.season, level=level)

    def add_standing(self, league, profile, points):
        return LeagueStanding.objects.create(
            league=league, player_profile=profile, league_points=Decimal(points)
        )

    def add_match(self, game, league, placements):
        """
        Creates one `SelectedGame` plus a `Result` per (profile, position) in
        `placements`, so the match's participant count equals len(placements).
        """
        picker = placements[0][0]
        selected_game = SelectedGame.objects.create(
            profile=picker, game=game, league=league
        )
        for profile, position in placements:
            Result.objects.create(
                player_profile=profile,
                selected_game=selected_game,
                league=league,
                season=self.season,
                position=position,
            )
        return selected_game


class CareerPerformanceTests(StatisticsServiceTestBase):
    def test_reaching_a_higher_league_outranks_all_lower_league_play(self):
        # A merely participated in L1 (0 points); B piled up points in L2 but
        # never reached L1; C earned points in L1.
        a = self.make_profile("A")
        b = self.make_profile("B")
        c = self.make_profile("C")

        l1 = self.make_league(1)
        l2 = self.make_league(2)
        self.add_standing(l1, a, 0)
        self.add_standing(l2, b, 50)
        self.add_standing(l1, c, 6)

        pool = _build_player_pool()
        ranked = _rank_career(pool)
        order = [entry["profile_id"] for entry in ranked]

        # C (L1, 6 pts) > A (L1, 0 pts) > B (L2 only), regardless of B's total.
        self.assertEqual(order, [c.id, a.id, b.id])
        self.assertEqual([entry["rank"] for entry in ranked], [1, 2, 3])

    def test_displayed_value_is_total_career_points(self):
        a = self.make_profile("A")
        l1 = self.make_league(1)
        l2 = self.make_league(2)
        self.add_standing(l1, a, 6)
        self.add_standing(l2, a, 3)

        ranked = _rank_career(_build_player_pool())
        self.assertEqual(ranked[0]["value"], 9)


class CategorySetTests(StatisticsServiceTestBase):
    def test_removed_categories_are_gone(self):
        profile = self.make_profile("solo")
        l1 = self.make_league(1)
        self.add_standing(l1, profile, 6)

        overview = get_statistics_overview(profile)
        keys = {category["key"] for category in overview["categories"]}

        self.assertEqual(
            keys,
            {"career_performance", "win_rate", "avg_position", "games_played"},
        )
        self.assertNotIn("total_wins", keys)
        self.assertNotIn("podiums", keys)
        self.assertNotIn("best_league_level", keys)

    def test_definitions_match_exposed_categories(self):
        keys = {definition["key"] for definition in CATEGORY_DEFS}
        self.assertEqual(
            keys,
            {"career_performance", "win_rate", "avg_position", "games_played"},
        )


class PlayerCountFilterTests(StatisticsServiceTestBase):
    def test_results_are_filtered_by_match_size(self):
        me = self.make_profile("me")
        o1 = self.make_profile("o1")
        o2 = self.make_profile("o2")
        o3 = self.make_profile("o3")

        game = Game.objects.create(name="G", platform=self.platform)
        big_league = self.make_league(1)
        small_league = self.make_league(2)

        # A 4-player match and a 2-player match, both involving `me`.
        self.add_match(game, big_league, [(me, 1), (o1, 2), (o2, 3), (o3, 4)])
        self.add_match(game, small_league, [(me, 1), (o1, 2)])

        all_games = _build_player_pool()
        me_all = next(p for p in all_games if p["profile_id"] == me.id)
        self.assertEqual(me_all["games_played"], 2)

        only_4p = _build_player_pool(player_counts=[4])
        me_4p = next(p for p in only_4p if p["profile_id"] == me.id)
        self.assertEqual(me_4p["games_played"], 1)

        only_2p = _build_player_pool(player_counts=[2])
        me_2p = next(p for p in only_2p if p["profile_id"] == me.id)
        self.assertEqual(me_2p["games_played"], 1)

    def test_standings_are_filtered_by_league_size(self):
        me = self.make_profile("me")
        others = [self.make_profile(f"o{i}") for i in range(3)]

        big_league = self.make_league(1)  # 4 members
        small_league = self.make_league(2)  # 2 members

        self.add_standing(big_league, me, 6)
        for other in others:
            self.add_standing(big_league, other, 1)

        self.add_standing(small_league, me, 3)
        self.add_standing(small_league, others[0], 0)

        only_4p = _build_player_pool(player_counts=[4])
        me_4p = next(p for p in only_4p if p["profile_id"] == me.id)
        # Only the 4-player league counts toward career points/levels.
        self.assertEqual(me_4p["league_points"], 6)
        self.assertEqual(me_4p["reached_levels"], {1})
