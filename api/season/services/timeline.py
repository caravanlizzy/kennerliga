from collections import defaultdict
from typing import Dict, List, Optional

from django.db.models import Count, Q

from game.models import BanDecision, SelectedGame
from league.models import League, LeagueStanding, LeagueTieResolution
from result.models import Result
from result.queries import get_game_records_map
from season.models import Season
from season.queries import get_open_season, get_running_season


def build_live_events_timeline(
    league_id: Optional[int] = None,
    season_id: Optional[int] = None,
    limit: Optional[int] = None,
) -> List[dict]:
    """
    Builds the live timeline of events (picks, bans, finishes) for a league or season.
    """
    if league_id:
        try:
            leagues = list(
                League.objects.filter(id=int(league_id)).annotate(
                    member_count=Count("members")
                )
            )
            if not leagues:
                return []
            season_id = leagues[0].season_id
        except (ValueError, TypeError):
            return []
    else:
        if not season_id:
            season = get_running_season()
            if not season:
                season = get_open_season()
            if not season:
                # Fallback to most recent season
                season = Season.objects.order_by("-year", "-month").first()
            if not season:
                return []
            season_id = season.id

        # Annotate member_count once instead of running .count() per league.
        leagues = list(
            League.objects.filter(season_id=season_id).annotate(
                member_count=Count("members")
            )
        )

    events = []

    # 1. PICK events
    picks = SelectedGame.objects.filter(league__in=leagues).select_related(
        "profile", "game", "league"
    )
    for pick in picks:
        events.append(
            {
                "id": f"pick-{pick.id}",
                "type": "PICK",
                "timestamp": pick.created_at,
                "leagueLevel": pick.league.level,
                "leagueId": pick.league.id,
                "data": {
                    "playerName": pick.profile.profile_name,
                    "gameName": pick.game.name,
                },
            }
        )

    # 2. BAN events
    bans = BanDecision.objects.filter(
        Q(league__in=leagues)
        & (Q(skipped_ban=True) | Q(selected_game__isnull=False))
    ).select_related("player_banning", "selected_game__game", "league")
    for ban in bans:
        game_name = ban.selected_game.game.name if ban.selected_game else None
        events.append(
            {
                "id": f"ban-{ban.id}",
                "type": "BAN",
                "timestamp": ban.created_at,
                "leagueLevel": ban.league.level,
                "leagueId": ban.league.id,
                "data": {
                    "playerName": ban.player_banning.profile_name,
                    "gameName": game_name,
                    "skippedBan": ban.skipped_ban,
                },
            }
        )

    # 3. LEAGUE_RUNNING events (picking/banning done; games actually played)
    running_statuses = {"PLAYING", "DONE"}
    picks_by_league: Dict[int, list] = defaultdict(list)
    for pick in picks:
        picks_by_league[pick.league_id].append(pick)
    bans_by_league: Dict[int, list] = defaultdict(list)
    for ban in bans:
        bans_by_league[ban.league_id].append(ban)

    for league in leagues:
        if league.status not in running_statuses:
            continue
        league_picks = picks_by_league.get(league.id, [])
        if not league_picks:
            continue

        member_count = league.member_count or 0
        min_bans = 2 if member_count > 2 else 1
        ban_counts_by_sg: Dict[int, int] = defaultdict(int)
        for b in bans_by_league.get(league.id, []):
            if b.selected_game_id is not None:
                ban_counts_by_sg[b.selected_game_id] += 1
        banned_sg_ids = {
            sg_id
            for sg_id, c in ban_counts_by_sg.items()
            if c >= min_bans
        }
        playing_picks = [p for p in league_picks if p.id not in banned_sg_ids]
        if not playing_picks:
            continue

        league_bans = bans_by_league.get(league.id, [])
        candidate_times = []
        for p in league_picks:
            candidate_times.append(p.created_at)
            if getattr(p, "updated_at", None):
                candidate_times.append(p.updated_at)
        for b in league_bans:
            candidate_times.append(b.created_at)
        event_time = max(candidate_times)

        games_payload = [
            {
                "playerName": p.profile.profile_name,
                "gameName": p.game.name,
            }
            for p in playing_picks
        ]

        events.append(
            {
                "id": f"league-running-{league.id}",
                "type": "LEAGUE_RUNNING",
                "timestamp": event_time,
                "leagueLevel": league.level,
                "leagueId": league.id,
                "data": {
                    "leagueLevel": league.level,
                    "games": games_payload,
                },
            }
        )

    # 4. GAME_FINISHED events
    game_records = get_game_records_map()

    results = Result.objects.filter(league__in=leagues).select_related(
        "player_profile", "selected_game__game", "league"
    )
    results_by_game = defaultdict(list)
    for r in results:
        results_by_game[r.selected_game_id].append(r)

    league_member_counts = {l.id: l.member_count for l in leagues}

    standings_by_league: Dict[int, list] = defaultdict(list)
    for ls in (
        LeagueStanding.objects.filter(league_id__in=[l.id for l in leagues])
        .select_related("player_profile")
        .order_by("-league_points", "-wins", "-second_places", "-third_places", "-tie_break_priority")
    ):
        standings_by_league[ls.league_id].append(ls)

    resolutions_by_league: Dict[int, list] = defaultdict(list)
    resolutions = (
        LeagueTieResolution.objects.filter(
            league_id__in=[l.id for l in leagues], is_resolved=True
        ).prefetch_related("entries__player_profile")
    )
    for res in resolutions:
        resolutions_by_league[res.league_id].append(res)

    for sg_id, res_list in results_by_game.items():
        if not res_list:
            continue
        league_id_val = res_list[0].league_id
        member_count = league_member_counts.get(league_id_val, 0)
        if len(res_list) == member_count and member_count > 0:
            last_result_time = max(r.created_at for r in res_list)

            full_results = sorted(
                res_list,
                key=lambda r: (
                    r.position is None,
                    r.position if r.position is not None else 10**9,
                    (r.player_profile.profile_name or ""),
                ),
            )

            min_pos = None
            winners = []
            for r in full_results:
                if r.position is None:
                    continue
                if min_pos is None:
                    min_pos = r.position
                if r.position == min_pos:
                    winners.append(r)
                else:
                    break

            primary_winner = (
                winners[0]
                if winners
                else (full_results[0] if full_results else None)
            )
            winners_names = (
                [w.player_profile.profile_name for w in winners]
                if winners
                else (
                    []
                    if primary_winner is None
                    else [primary_winner.player_profile.profile_name]
                )
            )
            game_id = res_list[0].selected_game.game_id
            rec_score = game_records.get(game_id)
            results_payload = [
                {
                    "playerName": r.player_profile.profile_name,
                    "position": r.position,
                    "points": r.points,
                    "is_record": (
                        r.points is not None
                        and rec_score is not None
                        and r.points >= 2
                        and r.points == rec_score
                    ),
                }
                for r in full_results
            ]

            has_record = any(r["is_record"] for r in results_payload)
            is_winner_record = (
                primary_winner.points is not None
                and rec_score is not None
                and primary_winner.points >= 2
                and primary_winner.points == rec_score
                if primary_winner
                else False
            )

            events.append(
                {
                    "id": f"finish-{sg_id}",
                    "type": "GAME_FINISHED",
                    "timestamp": last_result_time,
                    "leagueLevel": res_list[0].league.level,
                    "leagueId": league_id_val,
                    "data": {
                        "gameName": res_list[0].selected_game.game.name,
                        "winner": ", ".join(winners_names)
                        if winners_names
                        else None,
                        "winners": winners_names,
                        "points": primary_winner.points if primary_winner else None,
                        "is_record": is_winner_record,
                        "has_record": has_record,
                        "results": results_payload,
                    },
                }
            )

    # 5. LEAGUE_FINISHED events
    for league in leagues:
        if not league.is_finished:
            continue

        standings = standings_by_league.get(league.id, [])
        if not standings:
            continue

        top_standing = standings[0]
        winners = [
            s.player_profile.profile_name
            for s in standings
            if s.league_points == top_standing.league_points
            and s.wins == top_standing.wins
            and s.tie_break_priority == top_standing.tie_break_priority
        ]

        top_tie_players = [
            s.player_profile.profile_name
            for s in standings
            if s.league_points == top_standing.league_points
            and s.wins == top_standing.wins
        ]

        # Case A: Current tie needs a decider
        if len(winners) > 1:
            events.append(
                {
                    "id": f"league-decider-{league.id}",
                    "type": "LEAGUE_FINISHED",
                    "timestamp": league.updated_at,
                    "leagueLevel": league.level,
                    "leagueId": league.id,
                    "data": {"leagueLevel": league.level, "winners": winners},
                }
            )
        else:
            # Case B: Resolved tie or no tie from the start
            league_resolutions = resolutions_by_league.get(league.id, [])
            for res in league_resolutions:
                res_players = [
                    e.player_profile.profile_name for e in res.entries.all()
                ]
                if set(res_players) == set(top_tie_players) and len(res_players) > 1:
                    events.append(
                        {
                            "id": f"league-decider-{league.id}",
                            "type": "LEAGUE_FINISHED",
                            "timestamp": res.created_at,
                            "leagueLevel": league.level,
                            "leagueId": league.id,
                            "data": {
                                "leagueLevel": league.level,
                                "winners": res_players,
                            },
                        }
                    )
                    break

            events.append(
                {
                    "id": f"league-done-{league.id}",
                    "type": "LEAGUE_FINISHED",
                    "timestamp": league.updated_at,
                    "leagueLevel": league.level,
                    "leagueId": league.id,
                    "data": {"leagueLevel": league.level, "winners": winners},
                }
            )

    # 6. SEASON_FINISHED events
    if not league_id:
        season_obj = Season.objects.filter(id=season_id).first()
        if season_obj and season_obj.status == Season.SeasonStatus.DONE:
            l1 = next((l for l in leagues if l.level == 1), None)
            winner_name = "Unknown"
            if l1:
                l1_standings = standings_by_league.get(l1.id, [])
                if l1_standings:
                    winner_name = l1_standings[0].player_profile.profile_name

            events.append(
                {
                    "id": f"season-done-{season_obj.id}",
                    "type": "SEASON_FINISHED",
                    "timestamp": season_obj.updated_at,
                    "leagueId": None,
                    "data": {
                        "seasonName": f"{season_obj.year}-{season_obj.month:02d}",
                        "seasonWinner": winner_name,
                    },
                }
            )

    # Sort
    type_order = {
        "PICK": 0,
        "BAN": 0,
        "LEAGUE_RUNNING": 1,
        "GAME_FINISHED": 2,
        "LEAGUE_FINISHED": 3,
        "SEASON_FINISHED": 4,
    }
    events.sort(
        key=lambda x: (x["timestamp"], type_order.get(x["type"], 0)),
        reverse=True,
    )
    if limit:
        try:
            limit_val = int(limit)
            events = events[:limit_val]
        except (ValueError, TypeError):
            pass

    return events
