from decimal import Decimal

from django.test import TestCase

from game.models import (
    BanDecision,
    Game,
    ResultConfig,
    SelectedGame,
    StartingPointSystem,
)
from league.models import League, LeagueStanding
from result.models import Result
from season.models import Season
from statistic.services import (
    CATEGORY_DEFS,
    _build_player_pool,
    _rank_career,
    _rank_iron_will,
    get_awards,
    get_game_detailed_statistics,
    get_statistics_overview,
    get_win_suggestions,
)
from user.models import PlayerProfile, Platform, User


class StatisticsServiceTestBase(TestCase):
    def setUp(self):
        StartingPointSystem.objects.get_or_create(
            id=1, defaults={"code": "STD", "description": "Standard"}
        )
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
                "records",
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
                "records",
                "iron_will",
            },
        )


class RecordsPerformanceTests(StatisticsServiceTestBase):
    def add_match_with_points(self, game, league, placements_with_points, season=None):
        season = season or self.season
        picker = placements_with_points[0][0]
        selected_game = SelectedGame.objects.create(
            profile=picker, game=game, league=league
        )
        for profile, position, points in placements_with_points:
            Result.objects.create(
                player_profile=profile,
                selected_game=selected_game,
                league=league,
                season=season,
                position=position,
                points=points,
            )
        return selected_game

    def test_ranks_players_by_records_count(self):
        p_a = self.make_profile("A")
        p_b = self.make_profile("B")
        p_c = self.make_profile("C")

        g1 = Game.objects.create(name="Game 1", platform=self.platform)
        g2 = Game.objects.create(name="Game 2", platform=self.platform)
        g3 = Game.objects.create(name="Game 3", platform=self.platform)

        l1 = self.make_league(1)
        # G1: A gets 100 (record), B gets 80
        self.add_match_with_points(g1, l1, [(p_a, 1, 100), (p_b, 2, 80)])
        # G2: A gets 50 (record), C gets 30
        self.add_match_with_points(g2, l1, [(p_a, 1, 50), (p_c, 2, 30)])
        # G3: B gets 60 (record), C gets 40
        self.add_match_with_points(g3, l1, [(p_b, 1, 60), (p_c, 2, 40)])

        pool = _build_player_pool()
        overview = get_statistics_overview(p_a)
        records_cat = next(c for c in overview["categories"] if c["key"] == "records")

        # A has 2 records (G1, G2), B has 1 record (G3), C has 0 records
        self.assertEqual(
            [(entry["profile_id"], entry["rank"], entry["value"]) for entry in records_cat["top"]],
            [(p_a.id, 1, 2), (p_b.id, 2, 1), (p_c.id, 3, 0)],
        )

    def test_record_in_same_game_multiple_times_deduplicated(self):
        p_a = self.make_profile("A")
        p_b = self.make_profile("B")
        g1 = Game.objects.create(name="Game 1", platform=self.platform)
        l1 = self.make_league(1)
        l2 = self.make_league(2)

        # Match 1 in league 1: A scores 100, B scores 50
        self.add_match_with_points(g1, l1, [(p_a, 1, 100), (p_b, 2, 50)])
        # Match 2 in league 2: A scores 100 again (matches record)
        self.add_match_with_points(g1, l2, [(p_a, 1, 100), (p_b, 2, 60)])

        overview = get_statistics_overview(p_a)
        records_cat = next(c for c in overview["categories"] if c["key"] == "records")
        entry_a = next(e for e in records_cat["top"] if e["profile_id"] == p_a.id)

        # A only holds 1 record (for Game 1)
        self.assertEqual(entry_a["value"], 1)

    def test_shared_record_tie(self):
        p_a = self.make_profile("A")
        p_b = self.make_profile("B")
        g1 = Game.objects.create(name="Game 1", platform=self.platform)
        l1 = self.make_league(1)

        # Both A and B tie for the record score 100
        self.add_match_with_points(g1, l1, [(p_a, 1, 100), (p_b, 1, 100)])

        overview = get_statistics_overview(p_a)
        records_cat = next(c for c in overview["categories"] if c["key"] == "records")

        entry_a = next(e for e in records_cat["top"] if e["profile_id"] == p_a.id)
        entry_b = next(e for e in records_cat["top"] if e["profile_id"] == p_b.id)

        self.assertEqual(entry_a["value"], 1)
        self.assertEqual(entry_b["value"], 1)
        self.assertEqual(entry_a["rank"], 1)
        self.assertEqual(entry_b["rank"], 1)

    def test_no_points_game_and_below_2_points_excluded(self):
        p_a = self.make_profile("A")
        p_b = self.make_profile("B")
        g_no_pts = Game.objects.create(name="No Pts Game", platform=self.platform)
        ResultConfig.objects.create(game=g_no_pts, has_points=False)
        g_low_pts = Game.objects.create(name="Low Pts Game", platform=self.platform)
        l1 = self.make_league(1)

        # Match in no-points game with points populated should be excluded
        self.add_match_with_points(g_no_pts, l1, [(p_a, 1, 50), (p_b, 2, 20)])
        # Match with 1 point (< 2) should be excluded
        self.add_match_with_points(g_low_pts, l1, [(p_a, 1, 1), (p_b, 2, 0)])

        overview = get_statistics_overview(p_a)
        records_cat = next(c for c in overview["categories"] if c["key"] == "records")

        entry_a = next(e for e in records_cat["top"] if e["profile_id"] == p_a.id)
        self.assertEqual(entry_a["value"], 0)

    def test_records_count_matches_all_time_game_records_across_filters(self):
        season_2025 = Season.objects.create(
            year=2025, month=1, status=Season.SeasonStatus.DONE
        )
        p_a = self.make_profile("A")
        p_b = self.make_profile("B")
        g1 = Game.objects.create(name="Game 1", platform=self.platform)
        g2 = Game.objects.create(name="Game 2", platform=self.platform)

        l_2025 = League.objects.create(season=season_2025, level=1)
        l_2026 = self.make_league(1)

        # In 2025, A sets all-time record on G1 (100 pts)
        self.add_match_with_points(g1, l_2025, [(p_a, 1, 100), (p_b, 2, 50)], season=season_2025)
        # In 2026, both play G1 (A scores 70, B scores 80) and G2 (B sets record with 90 pts)
        self.add_match_with_points(g1, l_2026, [(p_b, 1, 80), (p_a, 2, 70)], season=self.season)
        self.add_match_with_points(g2, l_2026, [(p_b, 1, 90), (p_a, 2, 60)], season=self.season)

        # In 2026 overview: A holds 1 all-time record (G1), B holds 1 all-time record (G2)
        overview_2026 = get_statistics_overview(p_a, years=[2026])
        records_2026 = next(c for c in overview_2026["categories"] if c["key"] == "records")

        entry_a = next(e for e in records_2026["top"] if e["profile_id"] == p_a.id)
        entry_b = next(e for e in records_2026["top"] if e["profile_id"] == p_b.id)
        self.assertEqual(entry_a["value"], 1)
        self.assertEqual(entry_b["value"], 1)

    def test_records_count_matches_across_player_counts(self):
        p_a = self.make_profile("A")
        p_b = self.make_profile("B")
        p_c = self.make_profile("C")
        p_d = self.make_profile("D")

        g1 = Game.objects.create(name="Game 1", platform=self.platform)
        g2 = Game.objects.create(name="Game 2", platform=self.platform)

        l1 = self.make_league(1)
        l2 = self.make_league(2)

        # 2-player match on G1: A sets all-time record (100 pts)
        self.add_match_with_points(g1, l1, [(p_a, 1, 100), (p_b, 2, 50)])
        # 4-player match on G2: A scores 40 on G1 in 4P, but all 4 players are active in 4P
        self.add_match_with_points(g2, l2, [(p_a, 1, 80), (p_b, 2, 50), (p_c, 3, 40), (p_d, 4, 30)])

        # When filtered to 4P: A still holds their 1 all-time game record (G1)
        overview_4p = get_statistics_overview(p_a, player_counts=[4])
        records_4p = next(c for c in overview_4p["categories"] if c["key"] == "records")

        entry_a = next(e for e in records_4p["top"] if e["profile_id"] == p_a.id)
        self.assertEqual(entry_a["value"], 2)  # A holds record on G1 (100) and G2 (80)

    def test_records_count_consistent_with_user_profile(self):
        from rest_framework.test import APIClient

        p_a = self.make_profile("A")
        g1 = Game.objects.create(name="Game 1", platform=self.platform)
        l1 = self.make_league(1)
        self.add_match_with_points(g1, l1, [(p_a, 1, 100)])

        client = APIClient()
        client.force_authenticate(user=p_a.user)
        response = client.get(f"/api/user/users/{p_a.user.id}/statistics/")
        self.assertEqual(response.status_code, 200)
        profile_records = response.data["records"]

        overview = get_statistics_overview(p_a)
        records_cat = next(c for c in overview["categories"] if c["key"] == "records")
        entry_a = next(e for e in records_cat["top"] if e["profile_id"] == p_a.id)

        self.assertEqual(len(profile_records), entry_a["value"])


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
        # A's Spammer value is 3 (their most-repeated game), while their
        # Inspirer value is 2 (2 distinct games picked).
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
            [(a.id, 2), (b.id, 1)],
        )

    def test_inspirer_award_ranks_by_distinct_picks(self):
        a = self.make_profile("A")
        b = self.make_profile("B")
        c = self.make_profile("C")
        catan = Game.objects.create(name="Catan", platform=self.platform)
        chess = Game.objects.create(name="Chess", platform=self.platform)
        carcassonne = Game.objects.create(name="Carcassonne", platform=self.platform)

        # A picks 3 distinct games across 3 leagues
        self.make_pick(self.make_league(1), a, catan)
        self.make_pick(self.make_league(2), a, chess)
        self.make_pick(self.make_league(3), a, carcassonne)

        # B picks Catan 3 times across 3 different leagues (1 distinct game)
        self.make_pick(self.make_league(4), b, catan)
        self.make_pick(self.make_league(5), b, catan)
        self.make_pick(self.make_league(6), b, catan)

        # C picks 2 distinct games across 2 different leagues
        self.make_pick(self.make_league(7), c, catan)
        self.make_pick(self.make_league(8), c, chess)

        awards = get_awards(a, top_n=5, window=1)
        inspirer = next(award for award in awards if award["key"] == "inspirer")

        self.assertEqual(
            [(entry["profile_id"], entry["value"]) for entry in inspirer["top"]],
            [(a.id, 3), (c.id, 2), (b.id, 1)],
        )

    def test_inspirer_award_excludes_banned_picks(self):
        a = self.make_profile("A")
        b = self.make_profile("B")
        catan = Game.objects.create(name="Catan", platform=self.platform)
        chess = Game.objects.create(name="Chess", platform=self.platform)
        mars = Game.objects.create(name="Terraforming Mars", platform=self.platform)

        l1 = self.make_league(1)
        part_a = self.season.participants.create(profile=a)
        part_b = self.season.participants.create(profile=b)
        l1.members.add(part_a, part_b)

        # In l1 (2 players -> 1 ban needed): A picks Catan, which B successfully bans.
        catan_pick = self.make_pick(l1, a, catan)
        BanDecision.objects.create(league=l1, player_banning=b, selected_game=catan_pick)

        # A repicks Chess in l1 (not banned).
        self.make_pick(l1, a, chess)

        # In l2: A picks Terraforming Mars.
        l2 = self.make_league(2)
        self.make_pick(l2, a, mars)

        awards = get_awards(a, top_n=5, window=1)
        inspirer = next(award for award in awards if award["key"] == "inspirer")

        # A should have 2 distinct picks (Chess and Mars), Catan does not count since it was banned.
        self.assertEqual(
            [(entry["profile_id"], entry["value"]) for entry in inspirer["top"]],
            [(a.id, 2)],
        )


class WinSuggestionsTests(StatisticsServiceTestBase):
    def setUp(self):
        super().setUp()
        self.next_level = 0
        self.hero = self.make_profile("Hero")
        self.rival = self.make_profile("Rival")
        self.catan = Game.objects.create(name="Catan", platform=self.platform)
        self.chess = Game.objects.create(name="Chess", platform=self.platform)

    def new_league(self):
        self.next_level += 1
        return self.make_league(self.next_level)

    def test_ranks_game_hero_beats_rival_at_first(self):
        for _ in range(3):
            self.add_match(self.catan, self.new_league(), [(self.hero, 1), (self.rival, 2)])
            self.add_match(self.chess, self.new_league(), [(self.hero, 2), (self.rival, 1)])

        suggestions = get_win_suggestions(self.hero, [self.rival])

        self.assertEqual([s["game_id"] for s in suggestions], [self.catan.id, self.chess.id])
        self.assertGreater(suggestions[0]["win_chance"], 50)
        self.assertLess(suggestions[1]["win_chance"], 50)
        self.assertEqual(suggestions[0]["wins"], 3)
        self.assertEqual(suggestions[0]["opponents"][0]["shared_matches"], 3)

    def test_uses_skill_prior_without_head_to_head(self):
        other = self.make_profile("Other")
        # Hero wins Catan against someone else; Rival always loses Catan.
        self.add_match(self.catan, self.new_league(), [(self.hero, 1), (other, 2)])
        self.add_match(self.catan, self.new_league(), [(self.rival, 2), (other, 1)])

        suggestions = get_win_suggestions(self.hero, [self.rival])

        self.assertEqual(len(suggestions), 1)
        self.assertEqual(suggestions[0]["opponents"][0]["shared_matches"], 0)
        self.assertGreater(suggestions[0]["win_chance"], 50)

    def test_skips_games_hero_never_played(self):
        self.add_match(self.chess, self.new_league(), [(self.rival, 1), (self.make_profile("X"), 2)])

        self.assertEqual(get_win_suggestions(self.hero, [self.rival]), [])

    def test_single_game_when_hero_never_played(self):
        self.add_match(self.chess, self.new_league(), [(self.rival, 1), (self.make_profile("X"), 2)])

        suggestions = get_win_suggestions(self.hero, [self.rival], game=self.chess)
        self.assertEqual(len(suggestions), 1)
        stat = suggestions[0]
        self.assertEqual(stat["game_id"], self.chess.id)
        self.assertEqual(stat["games_played"], 0)
        self.assertEqual(stat["wins"], 0)
        self.assertEqual(len(stat["opponents"]), 1)
        self.assertEqual(stat["opponents"][0]["profile_id"], self.rival.id)
        self.assertEqual(stat["opponents"][0]["opponent_games"], 1)
        self.assertLess(stat["win_chance"], 50)

    def test_win_suggestions_view_with_game_param(self):
        league = self.new_league()
        other = self.make_profile("Other")
        # Enroll rival and other into the league's season
        self.season.participants.create(profile=self.hero)
        self.season.participants.create(profile=self.rival)
        self.season.participants.create(profile=other)
        league.members.add(self.hero.season_participants.get(season=self.season))
        league.members.add(self.rival.season_participants.get(season=self.season))
        league.members.add(other.season_participants.get(season=self.season))

        self.add_match(self.catan, self.new_league(), [(self.hero, 1), (self.rival, 2)])

        from rest_framework.test import APIClient
        client = APIClient()
        client.force_authenticate(user=self.hero.user)

        response = client.get(f"/api/statistics/leagues/{league.id}/win-suggestions/?game={self.catan.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["game_id"], self.catan.id)
        self.assertEqual(response.data["wins"], 1)
        self.assertEqual(len(response.data["opponents"]), 2)


class GameDetailedStatisticsTests(StatisticsServiceTestBase):
    def setUp(self):
        super().setUp()
        self.alice = self.make_profile("Alice")
        self.bob = self.make_profile("Bob")
        self.charlie = self.make_profile("Charlie")
        self.game = Game.objects.create(name="Terraforming Mars", platform=self.platform)
        self.league = self.make_league(1)

    def test_empty_game_stats(self):
        stats = get_game_detailed_statistics(self.game, profile=self.alice)
        self.assertEqual(stats["game"]["name"], "Terraforming Mars")
        self.assertEqual(stats["overview"]["total_matches"], 0)
        self.assertEqual(stats["overview"]["distinct_players"], 0)
        self.assertIsNone(stats["records"]["high_score"])
        self.assertEqual(stats["leaderboard"], [])
        self.assertEqual(stats["recent_matches"], [])

    def test_records_and_superlatives(self):
        # Match 1: Alice (1st, 100 pts), Bob (2nd, 80 pts), Charlie (3rd, 60 pts)
        selected_game1 = SelectedGame.objects.create(
            profile=self.alice, game=self.game, league=self.league
        )
        Result.objects.create(
            player_profile=self.alice,
            selected_game=selected_game1,
            league=self.league,
            season=self.season,
            position=1,
            points=100,
        )
        Result.objects.create(
            player_profile=self.bob,
            selected_game=selected_game1,
            league=self.league,
            season=self.season,
            position=2,
            points=80,
        )
        Result.objects.create(
            player_profile=self.charlie,
            selected_game=selected_game1,
            league=self.league,
            season=self.season,
            position=3,
            points=60,
        )

        # Match 2: Bob (1st, 120 pts), Alice (2nd, 90 pts) in League 2
        league2 = self.make_league(2)
        selected_game2 = SelectedGame.objects.create(
            profile=self.bob, game=self.game, league=league2
        )
        Result.objects.create(
            player_profile=self.bob,
            selected_game=selected_game2,
            league=league2,
            season=self.season,
            position=1,
            points=120,
        )
        Result.objects.create(
            player_profile=self.alice,
            selected_game=selected_game2,
            league=league2,
            season=self.season,
            position=2,
            points=90,
        )

        # Ban: Charlie bans this game in League 3
        league3 = self.make_league(3)
        selected_game3 = SelectedGame.objects.create(
            profile=self.charlie, game=self.game, league=league3
        )
        BanDecision.objects.create(
            league=league3,
            player_banning=self.charlie,
            selected_game=selected_game3,
            skipped_ban=False,
        )

        stats = get_game_detailed_statistics(self.game, profile=self.alice)

        # Overview
        self.assertEqual(stats["overview"]["total_matches"], 2)
        self.assertEqual(stats["overview"]["distinct_players"], 3)
        self.assertEqual(stats["overview"]["total_picks"], 3)
        self.assertEqual(stats["overview"]["total_bans"], 1)

        # Records
        self.assertIsNotNone(stats["records"]["high_score"])
        self.assertEqual(stats["records"]["high_score"]["points"], 120)
        self.assertEqual(stats["records"]["high_score"]["profile_name"], "Bob")
        self.assertEqual(stats["records"]["low_score"], 60)
        self.assertEqual(stats["records"]["avg_score"], 90.0) # (100+80+60+120+90)/5 = 90
        self.assertEqual(stats["records"]["avg_winning_score"], 110.0) # (100+120)/2 = 110

        # Superlatives
        self.assertEqual(stats["superlatives"]["most_banned_by"][0]["profile_name"], "Charlie")
        self.assertEqual(stats["superlatives"]["most_banned_by"][0]["count"], 1)

        # Leaderboard
        self.assertEqual(len(stats["leaderboard"]), 3)
        alice_entry = next(p for p in stats["leaderboard"] if p["profile_name"] == "Alice")
        self.assertTrue(alice_entry["is_me"])
        self.assertEqual(alice_entry["games_played"], 2)
        self.assertEqual(alice_entry["wins"], 1)
        self.assertEqual(alice_entry["best_score"], 100)

        # Recent matches
        self.assertEqual(len(stats["recent_matches"]), 2)
        self.assertEqual(len(stats["recent_matches"][0]["participants"]), 2)

    def test_api_view_endpoint(self):
        from rest_framework.test import APIClient
        client = APIClient()
        client.force_authenticate(user=self.alice.user)

        response = client.get(f"/api/statistics/games/{self.game.id}/details/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["game"]["id"], self.game.id)
        self.assertIn("records", response.data)
        self.assertIn("superlatives", response.data)
        self.assertIn("leaderboard", response.data)
        self.assertIn("recent_matches", response.data)
