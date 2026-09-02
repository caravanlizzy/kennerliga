from decimal import Decimal

from django.test import TestCase

from game.models import BanDecision, Game, SelectedGame
from league.models import League, LeagueStanding
from result.models import Result
from season.models import Season
from statistic.services import (
    CATEGORY_DEFS,
    _build_player_pool,
    _rank_career,
    _rank_iron_will,
    get_awards,
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

    def make_ban(self, league, banner):
        """Records one ban by `banner` in `league` (one per league, per the model's unique constraint)."""
        game = Game.objects.create(
            name=f"banned-{banner.profile_name}-{league.level}", platform=self.platform
        )
        selected_game = SelectedGame.objects.create(profile=banner, game=game, league=league)
        return BanDecision.objects.create(
            league=league, player_banning=banner, selected_game=selected_game
        )

    def make_pick(self, league, picker, game):
        """Records `picker` picking `game` in `league` (one pick per game, per league)."""
        return SelectedGame.objects.create(profile=picker, game=game, league=league)


class CareerPerformanceTests(StatisticsServiceTestBase):
    def test_total_career_points_determine_ranking(self):
        # League level no longer affects career rank: total points decide it.
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

        self.assertEqual(order, [b.id, c.id, a.id])
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
            {
                "career_performance",
                "win_rate",
                "avg_position",
                "games_played",
                "iron_will",
            },
        )
        self.assertNotIn("total_wins", keys)
        self.assertNotIn("podiums", keys)
        self.assertNotIn("best_league_level", keys)

    def test_definitions_match_exposed_categories(self):
        keys = {definition["key"] for definition in CATEGORY_DEFS}
        self.assertEqual(
            keys,
            {
                "career_performance",
                "win_rate",
                "avg_position",
                "games_played",
                "iron_will",
            },
        )


class IronWillTests(StatisticsServiceTestBase):
    def test_ranks_below_median_win_rate_players_by_games_played(self):
        winner = self.make_profile("Winner")
        grinder = self.make_profile("Grinder")
        regular = self.make_profile("Regular")
        rookie = self.make_profile("Rookie")
        game = Game.objects.create(name="Catan", platform=self.platform)

        # The winner always takes 1st, so their 100% win rate sits well
        # above the median and they're excluded from Iron Will entirely.
        for opponent, count in [(grinder, 3), (regular, 2), (rookie, 1)]:
            for _ in range(count):
                league = self.make_league(1)
                self.add_match(game, league, [(winner, 1), (opponent, 2)])

        pool = _build_player_pool()
        ranked = _rank_iron_will(pool, min_games=0)

        self.assertEqual(
            [(entry["profile_id"], entry["rank"], entry["value"]) for entry in ranked],
            [(grinder.id, 1, 3), (regular.id, 2, 2), (rookie.id, 3, 1)],
        )
        self.assertNotIn(winner.id, [entry["profile_id"] for entry in ranked])

    def test_unranked_player_falls_back_to_games_played_not_win_rate(self):
        # Solo wins their only match (100% win rate), which keeps them above
        # the median and out of the ranking -- confirms the "so far" value
        # falls back to games played rather than raising or leaking a raw
        # win-rate number.
        solo = self.make_profile("Solo")
        other = self.make_profile("Other")
        game = Game.objects.create(name="Catan", platform=self.platform)
        league = self.make_league(1)
        self.add_match(game, league, [(solo, 1), (other, 2)])

        overview = get_statistics_overview(solo, top_n=5, window=1)
        iron_will = next(c for c in overview["categories"] if c["key"] == "iron_will")

        self.assertFalse(iron_will["me"]["eligible"])
        self.assertEqual(iron_will["me"]["value"], 1)


class PlayerCountFilterTests(StatisticsServiceTestBase):
    def test_unplaced_results_do_not_count_toward_performance(self):
        me = self.make_profile("me")
        opponent = self.make_profile("opponent")
        game = Game.objects.create(name="G", platform=self.platform)
        league = self.make_league(1)
        selected_game = SelectedGame.objects.create(profile=me, game=game, league=league)
        Result.objects.create(
            player_profile=me,
            selected_game=selected_game,
            league=league,
            season=self.season,
            position=1,
        )
        Result.objects.create(
            player_profile=opponent,
            selected_game=selected_game,
            league=league,
            season=self.season,
            position=None,
        )

        pool = _build_player_pool()
        me_stats = next(player for player in pool if player["profile_id"] == me.id)

        self.assertEqual(me_stats["games_played"], 1)
        self.assertEqual(me_stats["win_rate"], 100)
        self.assertNotIn(opponent.id, [player["profile_id"] for player in pool])

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


class AwardTests(StatisticsServiceTestBase):
    def test_hater_award_is_ranked_like_a_category(self):
        a = self.make_profile("A")
        b = self.make_profile("B")
        c = self.make_profile("C")
        leagues = [self.make_league(level) for level in range(1, 4)]

        # A bans in all three leagues (3 bans), B in two, C in one.
        for league in leagues:
            self.make_ban(league, a)
        for league in leagues[:2]:
            self.make_ban(league, b)
        self.make_ban(leagues[0], c)

        awards = get_awards(a, top_n=5, window=1)
        hater = next(award for award in awards if award["key"] == "hater")

        self.assertEqual(hater["better"], "higher")
        self.assertIsNone(hater["min_games"])
        self.assertEqual(hater["total_ranked"], 3)
        self.assertEqual(
            [(entry["profile_id"], entry["rank"], entry["value"]) for entry in hater["top"]],
            [(a.id, 1, 3), (b.id, 2, 2), (c.id, 3, 1)],
        )
        self.assertTrue(hater["me"]["eligible"])
        self.assertEqual(hater["me"]["rank"], 1)

    def test_player_with_no_bans_gets_an_unranked_me_row(self):
        a = self.make_profile("A")
        d = self.make_profile("D")
        league = self.make_league(1)
        self.make_ban(league, a)

        awards = get_awards(d, top_n=5, window=1)
        hater = next(award for award in awards if award["key"] == "hater")

        self.assertFalse(hater["me"]["eligible"])
        self.assertIsNone(hater["me"]["rank"])
        self.assertEqual(hater["me"]["value"], 0)
        self.assertEqual(hater["around_me"], [])

    def test_top_n_and_window_are_respected(self):
        a = self.make_profile("A")
        b = self.make_profile("B")
        c = self.make_profile("C")
        leagues = [self.make_league(level) for level in range(1, 4)]

        for league in leagues:
            self.make_ban(league, a)
        for league in leagues[:2]:
            self.make_ban(league, b)
        self.make_ban(leagues[0], c)

        awards = get_awards(c, top_n=1, window=1)
        hater = next(award for award in awards if award["key"] == "hater")

        # top_n=1 caps the podium, but the requesting player (rank 3, last)
        # still gets an "around me" window centered on their own rank.
        self.assertEqual([entry["profile_id"] for entry in hater["top"]], [a.id])
        self.assertEqual(
            [entry["profile_id"] for entry in hater["around_me"]], [b.id, c.id]
        )
        self.assertEqual(hater["me"]["rank"], 3)

    def test_spammer_award_ranks_by_most_repeated_single_game(self):
        a = self.make_profile("A")
        b = self.make_profile("B")
        catan = Game.objects.create(name="Catan", platform=self.platform)
        chess = Game.objects.create(name="Chess", platform=self.platform)
        leagues = [self.make_league(level) for level in range(1, 5)]

        # A picks Catan three times (across three leagues) and Chess once --
        # A's Spammer value is 3 (their most-repeated game), not 4 (their
        # total picks, which would be the Inspirer value instead).
        self.make_pick(leagues[0], a, catan)
        self.make_pick(leagues[1], a, catan)
        self.make_pick(leagues[2], a, catan)
        self.make_pick(leagues[3], a, chess)

        # B only ever picks Catan once.
        other_league = self.make_league(5)
        self.make_pick(other_league, b, catan)

        awards = get_awards(a, top_n=5, window=1)
        spammer = next(award for award in awards if award["key"] == "spammer")
        inspirer = next(award for award in awards if award["key"] == "inspirer")

        self.assertEqual(
            [(entry["profile_id"], entry["value"]) for entry in spammer["top"]],
            [(a.id, 3), (b.id, 1)],
        )
        self.assertEqual(spammer["top"][0]["display"], "3x Catan")
        # Sanity check that Spammer and Inspirer measure different things.
        self.assertEqual(
            [(entry["profile_id"], entry["value"]) for entry in inspirer["top"]],
            [(a.id, 4), (b.id, 1)],
        )
