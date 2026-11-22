from collections import defaultdict

from game.models import Game
from result.models import Result
from user.models import PlayerProfile

# Smoothing weights for `get_win_suggestions`: how many "virtual" plays the
# neutral prior (50% / average finish) counts for, so a single lucky win on a
# game does not outrank a solid record built over many plays.
WIN_SUGGESTION_SKILL_PRIOR = 2
WIN_SUGGESTION_H2H_PRIOR = 2


def get_win_suggestions(hero, opponents, game=None):
    """
    Ranks every game `hero` has played by their estimated chance to beat
    `opponents` (typically the other members of the current league), best
    first, so a picker can see where they stand the best chance.

    If `game` is supplied, calculates matchup stats specifically for that
    game, including games `hero` has not played yet.

    Per game and opponent, the chance is built in two steps:
      1. Skill prior: each player's average normalized finish on the game
         (1 = always first, 0 = always last), smoothed towards 0.5. The
         difference between hero and opponent shifts a 50% baseline.
      2. Head-to-head: every shared match where hero finished ahead (1),
         level (0.5) or behind (0) updates that prior, so direct results
         weigh in more the more often the two actually met.
    The game's `win_chance` is the average over all opponents, i.e. the
    expected share of opponents hero finishes ahead of.
    """
    opponent_ids = [p.id for p in opponents if p.id != hero.id]
    player_ids = {hero.id, *opponent_ids}

    relevant_matches = Result.objects.filter(
        player_profile_id__in=player_ids, position__isnull=False
    )
    if game is not None:
        relevant_matches = relevant_matches.filter(selected_game__game=game)

    relevant_match_ids = relevant_matches.values("selected_game_id")
    rows = list(
        Result.objects.filter(
            selected_game_id__in=relevant_match_ids, position__isnull=False
        ).values(
            "selected_game_id",
            "selected_game__game_id",
            "player_profile_id",
            "position",
        )
    )

    matches = defaultdict(list)
    for row in rows:
        matches[row["selected_game_id"]].append(row)

    # finishes[game_id][profile_id] -> list of normalized finishes
    finishes = defaultdict(lambda: defaultdict(list))
    # h2h[game_id][opponent_id] -> [hero score sum, shared matches]
    h2h = defaultdict(lambda: defaultdict(lambda: [0.0, 0]))
    hero_wins = defaultdict(int)

    for match_rows in matches.values():
        size = len(match_rows)
        if size < 2:
            continue
        game_id = match_rows[0]["selected_game__game_id"]
        positions = {}
        for row in match_rows:
            pid = row["player_profile_id"]
            if pid not in player_ids:
                continue
            positions[pid] = row["position"]
            finishes[game_id][pid].append(
                max(0.0, min(1.0, (size - row["position"]) / (size - 1)))
            )

        hero_pos = positions.get(hero.id)
        if hero_pos is None:
            continue
        if hero_pos == 1:
            hero_wins[game_id] += 1
        for opp_id in opponent_ids:
            opp_pos = positions.get(opp_id)
            if opp_pos is None:
                continue
            score = 1.0 if hero_pos < opp_pos else 0.5 if hero_pos == opp_pos else 0.0
            entry = h2h[game_id][opp_id]
            entry[0] += score
            entry[1] += 1

    def skill(values):
        return (sum(values) + 0.5 * WIN_SUGGESTION_SKILL_PRIOR) / (
            len(values) + WIN_SUGGESTION_SKILL_PRIOR
        )

    if game is not None:
        game_ids = [game.id]
        games = {game.id: game}
    else:
        game_ids = [gid for gid, by_player in finishes.items() if by_player.get(hero.id)]
        games = {
            g.id: g
            for g in Game.objects.filter(id__in=game_ids).select_related("platform")
        }

    opponent_map = {
        p.id: p for p in PlayerProfile.objects.filter(id__in=opponent_ids)
    }

    suggestions = []
    for game_id in game_ids:
        game_obj = games.get(game_id)
        if not game_obj:
            continue
        by_player = finishes[game_id]
        hero_finishes = by_player.get(hero.id, [])
        hero_skill = skill(hero_finishes)

        breakdown = []
        for opp_id in opponent_ids:
            opp_finishes = by_player.get(opp_id, [])
            prior = max(0.05, min(0.95, 0.5 + hero_skill - skill(opp_finishes)))
            score_sum, shared = h2h[game_id].get(opp_id, (0.0, 0))
            chance = (score_sum + prior * WIN_SUGGESTION_H2H_PRIOR) / (
                shared + WIN_SUGGESTION_H2H_PRIOR
            )
            opp = opponent_map.get(opp_id)
            breakdown.append(
                {
                    "profile_id": opp_id,
                    "profile_name": opp.profile_name if opp else None,
                    "chance": round(chance * 100, 1),
                    "shared_matches": shared,
                    "opponent_games": len(opp_finishes),
                }
            )

        win_chance = (
            sum(b["chance"] for b in breakdown) / len(breakdown)
            if breakdown
            else round(hero_skill * 100, 1)
        )
        suggestions.append(
            {
                "game_id": game_obj.id,
                "name": game_obj.name,
                "short_name": game_obj.short_name,
                "platform": game_obj.platform.name,
                "win_chance": round(win_chance, 1),
                "games_played": len(hero_finishes),
                "wins": hero_wins[game_id],
                "shared_matches": sum(b["shared_matches"] for b in breakdown),
                "opponents": breakdown,
            }
        )

    suggestions.sort(
        key=lambda s: (-s["win_chance"], -s["games_played"], s["name"].lower())
    )
    return suggestions
