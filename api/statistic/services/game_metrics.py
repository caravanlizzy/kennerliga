from django.db.models import Avg, Count, Max, Min, Q

from game.models import BanDecision, Game, ResultConfig, SelectedGame
from result.models import Result
from user.models import PlayerProfile

from .query_filters import (
    DEFAULT_GAME_MIN_GAMES,
    DEFAULT_POPULAR_GAMES_N,
    _filter_results_by_player_count,
    _filter_standings_by_player_count,
)


def _best_player_by_game(qs):
    """
    Ranks every player within each game by the same "most wins, then most
    consistent" ordering as `get_game_leaderboard` (win rate desc, avg
    position asc, games played desc, name asc), and keeps only the winner
    per game. A single grouped query, rather than one `get_game_leaderboard`
    call per game, so the game picker can show a "best player" preview for
    every game at once.
    """
    rows = qs.values("selected_game__game_id", "player_profile_id").annotate(
        games_played=Count("id"),
        wins=Count("id", filter=Q(position=1)),
        avg_position=Avg("position"),
    )

    profile_map = {
        p.id: p
        for p in PlayerProfile.objects.filter(
            id__in={row["player_profile_id"] for row in rows}
        ).select_related("user")
    }

    best_by_game = {}
    for row in rows:
        game_id = row["selected_game__game_id"]
        player = profile_map.get(row["player_profile_id"])
        if game_id is None or not player:
            continue
        played = row["games_played"] or 0
        wins = row["wins"] or 0
        win_rate = round(wins / played * 100, 1) if played > 0 else None
        avg_position = (
            round(float(row["avg_position"]), 2)
            if row["avg_position"] is not None
            else None
        )
        sort_key = (
            -(win_rate or 0),
            avg_position if avg_position is not None else float("inf"),
            -played,
            player.profile_name.lower(),
        )
        best = best_by_game.get(game_id)
        if best is None or sort_key < best[0]:
            best_by_game[game_id] = (
                sort_key,
                {
                    "profile_id": player.id,
                    "profile_name": player.profile_name,
                    "win_rate": win_rate,
                    "avg_position": avg_position,
                },
            )

    return {game_id: entry[1] for game_id, entry in best_by_game.items()}


def get_popular_games(years=None, player_counts=None, top_n=DEFAULT_POPULAR_GAMES_N):
    """
    Returns the most picked and most banned games (top N each), so the games
    statistics section can lead with an at-a-glance podium of which games get
    chosen most and which get vetoed most before drilling into a single
    game's leaderboard. Respects the same year/player-count filters as the
    rest of the dashboard.
    """
    pick_qs = SelectedGame.objects.all()
    if years:
        pick_qs = pick_qs.filter(league__season__year__in=years)
    pick_qs = _filter_standings_by_player_count(pick_qs, player_counts)
    picked_rows = (
        pick_qs.values("game_id", "game__name", "game__platform__name")
        .annotate(count=Count("id"))
        .order_by("-count", "game__name")[:top_n]
    )

    ban_qs = BanDecision.objects.filter(skipped_ban=False, selected_game__isnull=False)
    if years:
        ban_qs = ban_qs.filter(league__season__year__in=years)
    ban_qs = _filter_standings_by_player_count(ban_qs, player_counts)
    banned_rows = (
        ban_qs.values(
            "selected_game__game_id",
            "selected_game__game__name",
            "selected_game__game__platform__name",
        )
        .annotate(count=Count("id"))
        .order_by("-count", "selected_game__game__name")[:top_n]
    )

    most_picked = [
        {
            "game_id": row["game_id"],
            "name": row["game__name"],
            "platform": row["game__platform__name"],
            "count": row["count"],
        }
        for row in picked_rows
    ]
    most_banned = [
        {
            "game_id": row["selected_game__game_id"],
            "name": row["selected_game__game__name"],
            "platform": row["selected_game__game__platform__name"],
            "count": row["count"],
        }
        for row in banned_rows
    ]
    return {"most_picked": most_picked, "most_banned": most_banned}


def list_games_with_stats(years=None, player_counts=None):
    """
    Returns every game that has at least one recorded result, with basic
    popularity stats and the current best player, for use as a searchable
    picker for the per-game leaderboard.
    """
    qs = Result.objects.filter(position__isnull=False).select_related(
        "selected_game__game__platform"
    )
    if years:
        qs = qs.filter(season__year__in=years)
    qs = _filter_results_by_player_count(qs, player_counts)

    rows = (
        qs.values(
            "selected_game__game_id",
            "selected_game__game__name",
            "selected_game__game__platform__name",
        )
        .annotate(
            games_played=Count("id"),
            distinct_players=Count("player_profile", distinct=True),
        )
        .order_by("-games_played", "selected_game__game__name")
    )

    best_players = _best_player_by_game(qs)

    return [
        {
            "game_id": row["selected_game__game_id"],
            "name": row["selected_game__game__name"],
            "platform": row["selected_game__game__platform__name"],
            "games_played": row["games_played"],
            "distinct_players": row["distinct_players"],
            "best_player": best_players.get(row["selected_game__game_id"]),
        }
        for row in rows
        if row["selected_game__game_id"] is not None
    ]


def get_game_leaderboard(
    game, profile, years=None, player_counts=None, min_games=DEFAULT_GAME_MIN_GAMES
):
    """
    Ranks every player who has played `game`, ordered by win rate (desc)
    then average position (asc) as a tie-break -- the same "most wins, then
    most consistent" ordering already used to pick a player's `top_games` in
    `user.views.UserViewSet.user_statistics`. Players below `min_games` are
    excluded from the ranking (too few games to mean anything) but the
    requesting player's own row is always returned separately via `me`.
    """
    qs = Result.objects.filter(selected_game__game=game, position__isnull=False)
    if years:
        qs = qs.filter(season__year__in=years)
    qs = _filter_results_by_player_count(qs, player_counts)

    rows = qs.values("player_profile_id").annotate(
        games_played=Count("id"),
        wins=Count("id", filter=Q(position=1)),
        avg_position=Avg("position"),
    )

    profile_map = {
        p.id: p
        for p in PlayerProfile.objects.filter(
            id__in=[row["player_profile_id"] for row in rows]
        ).select_related("user")
    }

    players = []
    for row in rows:
        p = profile_map.get(row["player_profile_id"])
        if not p:
            continue
        played = row["games_played"] or 0
        wins = row["wins"] or 0
        players.append(
            {
                "profile_id": p.id,
                "profile_name": p.profile_name,
                "username": p.user.username if p.user else None,
                "games_played": played,
                "wins": wins,
                "avg_position": (
                    round(float(row["avg_position"]), 2)
                    if row["avg_position"] is not None
                    else None
                ),
                "win_rate": round(wins / played * 100, 1) if played > 0 else None,
            }
        )

    eligible = [p for p in players if p["games_played"] >= min_games]
    excluded_low_sample_count = len(players) - len(eligible)

    def sort_key(player):
        return (
            -(player["win_rate"] or 0),
            player["avg_position"] if player["avg_position"] is not None else float("inf"),
            -player["games_played"],
            player["profile_name"].lower(),
        )

    eligible.sort(key=sort_key)

    leaderboard = []
    rank = 0
    previous_key = None
    for player in eligible:
        key = (player["win_rate"], player["avg_position"])
        if key != previous_key:
            rank += 1
            previous_key = key
        leaderboard.append(
            {
                **player,
                "rank": rank,
                "is_me": player["profile_id"] == profile.id,
                "eligible": True,
            }
        )

    me_entry = next((row for row in leaderboard if row["profile_id"] == profile.id), None)
    if me_entry is None:
        raw = next((p for p in players if p["profile_id"] == profile.id), None)
        me_entry = {
            **(raw or {
                "profile_id": profile.id,
                "profile_name": profile.profile_name,
                "username": profile.user.username if profile.user else None,
                "games_played": 0,
                "wins": 0,
                "avg_position": None,
                "win_rate": None,
            }),
            "rank": None,
            "is_me": True,
            "eligible": False,
        }

    return {
        "game_id": game.id,
        "name": game.name,
        "platform": game.platform.name,
        "min_games": min_games,
        "excluded_low_sample_count": excluded_low_sample_count,
        "leaderboard": leaderboard,
        "me": me_entry,
    }


def get_game_detailed_statistics(
    game, profile=None, years=None, player_counts=None, min_games=0
):
    """
    Returns comprehensive statistics and details for a single game:
      - Game metadata & result configuration
      - High-level overview (total matches, distinct players, seasons, picks, bans)
      - Records (high score with holder & match details, low score, avg score, avg winning score)
      - Superlatives (most picked by, most banned by, most wins by, most played by)
      - Player Leaderboard (rank, profile, games played, wins, win rate, avg position, best score)
      - Faction statistics (if factions exist)
      - Recent match history
    """
    # 1. Game metadata and configuration
    rc = (
        ResultConfig.objects.filter(game=game)
        .select_related("starting_points_system")
        .first()
    )
    win_conditions = (
        [wc.name for wc in rc.win_conditions.all()] if rc else []
    )
    tie_breakers = [
        tb.name
        for wc in (rc.win_conditions.prefetch_related("tie_breakers").all() if rc else [])
        for tb in wc.tie_breakers.all()
    ]
    game_factions = list(game.faction_set.all())
    game_data = {
        "id": game.id,
        "name": game.name,
        "short_name": game.short_name,
        "platform": {
            "id": game.platform.id,
            "name": game.platform.name,
        },
        "min_players": game.min_players,
        "max_players": game.max_players,
        "selectable": game.selectable,
        "has_points": rc.has_points if rc else True,
        "is_asymmetric": rc.is_asymmetric if rc else False,
        "has_starting_player_order": rc.has_starting_player_order if rc else True,
        "starting_points_system": (
            rc.starting_points_system.description
            if rc and rc.starting_points_system
            else None
        ),
        "win_conditions": win_conditions,
        "tie_breakers": tie_breakers,
        "options": [
            {
                "id": opt.id,
                "name": opt.name,
                "choices": [c.name for c in opt.choices.all()],
            }
            for opt in game.options.all().prefetch_related("choices")
        ],
        "factions": [{"id": f.id, "name": f.name} for f in game_factions],
    }

    # 2. Results & Picks/Bans QuerySets with filter support
    results_qs = Result.objects.filter(
        selected_game__game=game, position__isnull=False
    )
    picks_qs = SelectedGame.objects.filter(game=game)
    bans_qs = BanDecision.objects.filter(
        selected_game__game=game, skipped_ban=False
    )

    if years:
        results_qs = results_qs.filter(season__year__in=years)
        picks_qs = picks_qs.filter(league__season__year__in=years)
        bans_qs = bans_qs.filter(league__season__year__in=years)

    results_qs = _filter_results_by_player_count(results_qs, player_counts)
    picks_qs = _filter_standings_by_player_count(picks_qs, player_counts)
    bans_qs = _filter_standings_by_player_count(bans_qs, player_counts)

    # 3. Overview
    total_matches = results_qs.values("selected_game_id").distinct().count()
    distinct_players = results_qs.values("player_profile_id").distinct().count()
    distinct_seasons = results_qs.values("season_id").distinct().count()
    total_picks = picks_qs.count()
    total_bans = bans_qs.count()

    overview = {
        "total_matches": total_matches,
        "distinct_players": distinct_players,
        "distinct_seasons": distinct_seasons,
        "total_picks": total_picks,
        "total_bans": total_bans,
    }

    # 4. Records
    high_score_res = (
        results_qs.filter(points__isnull=False)
        .select_related("player_profile__user", "season", "league", "selected_game")
        .order_by("-points", "created_at")
        .first()
    )
    high_score = None
    if high_score_res:
        high_score = {
            "points": high_score_res.points,
            "profile_id": high_score_res.player_profile.id,
            "profile_name": high_score_res.player_profile.profile_name,
            "username": (
                high_score_res.player_profile.user.username
                if high_score_res.player_profile.user
                else None
            ),
            "match_id": high_score_res.selected_game_id,
            "season_id": high_score_res.season_id,
            "season_name": high_score_res.season.name,
            "league_id": high_score_res.league_id,
            "league_level": (
                high_score_res.league.level if high_score_res.league else None
            ),
            "league_name": (
                f"League {high_score_res.league.level}"
                if high_score_res.league
                else None
            ),
            "date": high_score_res.created_at,
        }

    low_score_val = results_qs.filter(points__isnull=False).aggregate(
        min_p=Min("points")
    )["min_p"]
    avg_score_val = results_qs.filter(points__isnull=False).aggregate(
        avg_p=Avg("points")
    )["avg_p"]
    avg_win_val = results_qs.filter(position=1, points__isnull=False).aggregate(
        avg_p=Avg("points")
    )["avg_p"]

    records = {
        "high_score": high_score,
        "low_score": low_score_val,
        "avg_score": round(float(avg_score_val), 1) if avg_score_val is not None else None,
        "avg_winning_score": (
            round(float(avg_win_val), 1) if avg_win_val is not None else None
        ),
    }

    # 5. Superlatives
    most_picked_rows = (
        picks_qs.values(
            "profile_id",
            "profile__profile_name",
            "profile__user__username",
        )
        .annotate(count=Count("id"))
        .order_by("-count", "profile__profile_name")[:3]
    )
    most_picked_by = [
        {
            "profile_id": row["profile_id"],
            "profile_name": row["profile__profile_name"],
            "username": row["profile__user__username"],
            "count": row["count"],
        }
        for row in most_picked_rows
    ]

    most_banned_rows = (
        bans_qs.values(
            "player_banning_id",
            "player_banning__profile_name",
            "player_banning__user__username",
        )
        .annotate(count=Count("id"))
        .order_by("-count", "player_banning__profile_name")[:3]
    )
    most_banned_by = [
        {
            "profile_id": row["player_banning_id"],
            "profile_name": row["player_banning__profile_name"],
            "username": row["player_banning__user__username"],
            "count": row["count"],
        }
        for row in most_banned_rows
    ]

    most_wins_rows = (
        results_qs.filter(position=1)
        .values(
            "player_profile_id",
            "player_profile__profile_name",
            "player_profile__user__username",
        )
        .annotate(count=Count("id"))
        .order_by("-count", "player_profile__profile_name")[:3]
    )
    most_wins_by = [
        {
            "profile_id": row["player_profile_id"],
            "profile_name": row["player_profile__profile_name"],
            "username": row["player_profile__user__username"],
            "count": row["count"],
        }
        for row in most_wins_rows
    ]

    most_played_rows = (
        results_qs.values(
            "player_profile_id",
            "player_profile__profile_name",
            "player_profile__user__username",
        )
        .annotate(count=Count("id"))
        .order_by("-count", "player_profile__profile_name")[:3]
    )
    most_played_by = [
        {
            "profile_id": row["player_profile_id"],
            "profile_name": row["player_profile__profile_name"],
            "username": row["player_profile__user__username"],
            "count": row["count"],
        }
        for row in most_played_rows
    ]

    superlatives = {
        "most_picked_by": most_picked_by,
        "most_banned_by": most_banned_by,
        "most_wins_by": most_wins_by,
        "most_played_by": most_played_by,
    }

    # 6. Leaderboard
    player_stats_rows = (
        results_qs.values("player_profile_id")
        .annotate(
            games_played=Count("id"),
            wins=Count("id", filter=Q(position=1)),
            avg_position=Avg("position"),
            best_score=Max("points"),
            avg_score=Avg("points"),
        )
    )
    profile_map = {
        p.id: p
        for p in PlayerProfile.objects.filter(
            id__in=[r["player_profile_id"] for r in player_stats_rows]
        ).select_related("user")
    }
    leaderboard = []
    for r in player_stats_rows:
        p = profile_map.get(r["player_profile_id"])
        if not p:
            continue
        played = r["games_played"] or 0
        wins = r["wins"] or 0
        win_rate = round(wins / played * 100, 1) if played > 0 else 0.0
        avg_pos = (
            round(float(r["avg_position"]), 2)
            if r["avg_position"] is not None
            else None
        )
        avg_sc = (
            round(float(r["avg_score"]), 1)
            if r["avg_score"] is not None
            else None
        )
        leaderboard.append(
            {
                "profile_id": p.id,
                "profile_name": p.profile_name,
                "username": p.user.username if p.user else None,
                "games_played": played,
                "wins": wins,
                "win_rate": win_rate,
                "avg_position": avg_pos,
                "best_score": r["best_score"],
                "avg_score": avg_sc,
                "is_me": (profile is not None and p.id == profile.id),
                "eligible": played >= min_games,
            }
        )

    # Sort: eligible first, win_rate desc, avg_position asc, games_played desc
    eligible_players = [p for p in leaderboard if p["eligible"]]
    ineligible_players = [p for p in leaderboard if not p["eligible"]]

    eligible_players.sort(
        key=lambda x: (
            -x["win_rate"],
            x["avg_position"] if x["avg_position"] is not None else 9999,
            -x["games_played"],
            x["profile_name"].lower(),
        )
    )
    for idx, entry in enumerate(eligible_players, start=1):
        entry["rank"] = idx

    ineligible_players.sort(
        key=lambda x: (
            -x["games_played"],
            -x["win_rate"],
            x["profile_name"].lower(),
        )
    )
    for entry in ineligible_players:
        entry["rank"] = None

    sorted_leaderboard = eligible_players + ineligible_players

    # 7. Faction stats
    faction_stats = []
    for f in game_factions:
        f_results = results_qs.filter(Q(faction=f) | Q(factions=f)).distinct()
        f_played = f_results.count()
        if f_played > 0:
            f_wins = f_results.filter(position=1).count()
            f_win_rate = round(f_wins / f_played * 100, 1)
            f_avg_pos = f_results.aggregate(avg=Avg("position"))["avg"]
            f_avg_pts = f_results.filter(points__isnull=False).aggregate(
                avg=Avg("points")
            )["avg"]
            f_best_pts = f_results.filter(points__isnull=False).aggregate(
                max=Max("points")
            )["max"]
            faction_stats.append(
                {
                    "id": f.id,
                    "name": f.name,
                    "icon": getattr(f, "icon", None),
                    "games_played": f_played,
                    "wins": f_wins,
                    "win_rate": f_win_rate,
                    "avg_position": (
                        round(float(f_avg_pos), 2) if f_avg_pos is not None else None
                    ),
                    "avg_points": (
                        round(float(f_avg_pts), 1) if f_avg_pts is not None else None
                    ),
                    "best_score": f_best_pts,
                }
            )
        else:
            faction_stats.append(
                {
                    "id": f.id,
                    "name": f.name,
                    "icon": getattr(f, "icon", None),
                    "games_played": 0,
                    "wins": 0,
                    "win_rate": 0.0,
                    "avg_position": None,
                    "avg_points": None,
                    "best_score": None,
                }
            )
    faction_stats.sort(key=lambda x: (-x["games_played"], -x["win_rate"], x["name"].lower()))

    # 8. Recent matches
    match_ids = list(
        results_qs.values_list("selected_game_id", flat=True)
        .distinct()
        .order_by("-selected_game__created_at")[:25]
    )
    selected_games = (
        SelectedGame.objects.filter(id__in=match_ids)
        .select_related("league", "league__season", "profile__user")
        .prefetch_related(
            "result_set__player_profile__user",
            "result_set__faction",
            "result_set__win_condition",
            "selected_options__game_option",
            "selected_options__choice",
        )
        .order_by("-created_at")
    )
    recent_matches = []
    for sg in selected_games:
        sg_results = list(
            sg.result_set.filter(position__isnull=False).order_by("position", "-points")
        )
        participants = [
            {
                "profile_id": r.player_profile.id,
                "profile_name": r.player_profile.profile_name,
                "username": (
                    r.player_profile.user.username
                    if r.player_profile.user
                    else None
                ),
                "position": r.position,
                "points": r.points,
                "faction_name": r.faction.name if r.faction else None,
                "win_condition_name": (
                    r.win_condition.name if r.win_condition else None
                ),
                "is_winner": r.position == 1,
            }
            for r in sg_results
        ]
        options_selected = [
            {
                "option_name": so.game_option.name if so.game_option else "",
                "choice_name": (
                    so.choice.name
                    if so.choice
                    else ("Yes" if so.value else "No" if so.value is not None else "")
                ),
            }
            for so in sg.selected_options.all()
        ]
        recent_matches.append(
            {
                "id": sg.id,
                "season_id": (
                    sg.league.season.id if sg.league and sg.league.season else None
                ),
                "season_name": (
                    sg.league.season.name
                    if sg.league and sg.league.season
                    else None
                ),
                "season_year": (
                    sg.league.season.year
                    if sg.league and sg.league.season
                    else None
                ),
                "league_id": sg.league.id if sg.league else None,
                "league_level": sg.league.level if sg.league else None,
                "league_name": (
                    f"League {sg.league.level}" if sg.league else None
                ),
                "date": sg.created_at,
                "participants": participants,
                "selected_options": options_selected,
            }
        )

    return {
        "game": game_data,
        "overview": overview,
        "records": records,
        "superlatives": superlatives,
        "leaderboard": sorted_leaderboard,
        "factions": faction_stats,
        "recent_matches": recent_matches,
    }
