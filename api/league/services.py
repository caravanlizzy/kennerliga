from typing import Optional, List, Dict, Iterable
from django.db import transaction
from django.db.models import Count, Prefetch
from game.models import SelectedGame, BanDecision, ResultConfig
from league.models import (
    League,
    LeagueStatus,
    LeagueStanding,
    GameStanding,
    LeagueTieResolution,
)
from season.models import SeasonParticipant
from league import queries as q
from api.constants import get_ban_amount_for_success


def _serialize_selected_game(sg) -> Dict:
    configs = list(sg.game.resultconfig_set.all())
    return {
        "id": sg.id,
        "game_name": sg.game.name,
        "game_short_name": sg.game.short_name,
        "platform_name": sg.game.platform.name,
        "has_points": configs[0].has_points if configs else True,
        "selected_by_id": sg.profile.id if sg.profile else None,
        "selected_by_name": sg.profile.profile_name if sg.profile else None,
    }


def _gs_row(gs) -> Dict:
    return {
        "points": str(gs.points),
        "league_points": str(gs.league_points),
        "rank": gs.rank,
        "decisive_tie_breaker_name": gs.decisive_tie_breaker.name
        if gs.decisive_tie_breaker
        else None,
        "tie_breaker_value": gs.tie_breaker_value,
    }


def build_full_standings_payload(
    league: League,
    selected_games: List,
    league_standing_list: List,
    game_standings: Iterable,
    members: Iterable,
    tie_resolutions: Iterable,
) -> Dict:
    """Build the full-standings payload for one league from pre-loaded data.

    All inputs are expected to already be filtered to this league. This keeps
    the function reusable between the per-league endpoint and the batched
    season-wide endpoint, where data is bulk-loaded once and grouped by
    league_id.
    """
    selected_game_list = [_serialize_selected_game(sg) for sg in selected_games]
    selected_game_ids = [sg.id for sg in selected_games]

    league_standing_dict = {ls.player_profile_id: ls for ls in league_standing_list}

    # Build a lookup: {player_profile_id: {selected_game_id: {...}}}
    game_data_by_player: Dict[int, Dict[int, Dict]] = {}
    for gs in game_standings:
        game_data_by_player.setdefault(gs.player_profile_id, {})[
            gs.selected_game_id
        ] = _gs_row(gs)

    # 5. Build the response rows
    standings_list = []
    for member in members:
        pid = member.profile_id
        ls = league_standing_dict.get(pid)
        player_games = game_data_by_player.get(pid, {})

        games_dict = {}
        for sg_id in selected_game_ids:
            if sg_id in player_games:
                games_dict[str(sg_id)] = player_games[sg_id]
            else:
                games_dict[str(sg_id)] = {
                    "points": None,
                    "league_points": None,
                    "rank": None,
                }

        standings_list.append(
            {
                "player_profile_id": pid,
                "profile_name": member.profile.profile_name,
                "user_id": member.profile.user.id if member.profile.user else None,
                "username": member.profile.user.username
                if member.profile.user
                else None,
                "total_league_points": str(ls.league_points) if ls else "0",
                "total_wins": str(ls.wins) if ls else "0",
                "unresolved_tie_group": ls.unresolved_tie_group if ls else None,
                "games": games_dict,
            }
        )

    # Sort standings_list: if we have LeagueStandings, sort by them, otherwise stick to member rank
    if league_standing_list:
        standings_list.sort(
            key=lambda x: (
                -float(x["total_league_points"]),
                -float(x["total_wins"]),
                x["profile_name"],
            )
        )

    # 6. Build tie groups information (unresolved and resolved)
    # Unresolved groups from current snapshot - reuse already-loaded
    # ``league_standing_list`` instead of re-querying LeagueStanding.
    unresolved_map: Dict[str, Dict] = {}
    for ls in league_standing_list:
        key = ls.unresolved_tie_group
        if not key:
            continue
        if key not in unresolved_map:
            unresolved_map[key] = {
                "group_key": key,
                "unresolved": True,
                "members": [],
                # optional snapshot metrics (useful for UI hints)
                "league_points": str(ls.league_points),
                "wins": str(ls.wins),
                "resolution": None,
            }
        unresolved_map[key]["members"].append(
            {
                "player_profile_id": ls.player_profile_id,
                "profile_name": ls.player_profile.profile_name,
                "user_id": ls.player_profile.user.id
                if ls.player_profile.user
                else None,
                "username": ls.player_profile.user.username
                if ls.player_profile.user
                else None,
            }
        )

    # Resolutions (may include groups already resolved and thus not present as unresolved anymore)
    resolution_map: Dict[str, Dict] = {}
    for res in tie_resolutions:
        # Members ordered by order_index for display
        ordered_entries = sorted(res.entries.all(), key=lambda e: e.order_index)
        members = [
            {
                "player_profile_id": e.player_profile_id,
                "profile_name": e.player_profile.profile_name,
                "user_id": e.player_profile.user.id if e.player_profile.user else None,
                "username": e.player_profile.user.username
                if e.player_profile.user
                else None,
                "order_index": e.order_index,
            }
            for e in ordered_entries
        ]

        resolution_map[res.group_key] = {
            "group_key": res.group_key,
            "unresolved": False,
            "members": members,
            "resolution": {
                "reason": res.reason,
                "reason_display": res.get_reason_display(),
                "note": res.note,
                "is_resolved": res.is_resolved,
            },
        }

    # Merge: unresolved first, then add resolved groups that aren't currently unresolved
    tie_groups: List[Dict] = []

    # Add unresolved groups
    for key, group in unresolved_map.items():
        merged = group.copy()
        # If there is a resolution object, it's NOT unresolved anymore for the UI's "unresolved" badges
        # but it keeps its asterisk and reason.
        if key in resolution_map:
            merged["unresolved"] = not resolution_map[key]["resolution"]["is_resolved"]
            merged["resolution"] = resolution_map[key]["resolution"]
            # prefer current unresolved membership ordering; do not override members
        else:
            merged["unresolved"] = True

        tie_groups.append(merged)

    # Add purely resolved groups (no longer tied in snapshot points/wins - though this shouldn't happen with current snapshot logic)
    for key, group in resolution_map.items():
        if key not in unresolved_map:
            tie_groups.append(group)

    # Stable sort: unresolved groups first by points/wins desc, then resolved by group_key
    def _tg_sort_key(g):
        if g.get("unresolved"):
            return (
                0,
                -(float(g.get("league_points") or 0)),
                -(float(g.get("wins") or 0)),
                g["group_key"],
            )
        return (1, 0, 0, g["group_key"])

    tie_groups.sort(key=_tg_sort_key)

    return {
        "selected_games": selected_game_list,
        "standings": standings_list,
        "season_id": league.season_id,
        "tie_groups": tie_groups,
    }


def _selected_games_qs(league_filter):
    """SelectedGame queryset with the lean ResultConfig prefetch."""
    return (
        SelectedGame.objects.filter(**league_filter)
        .annotate(ban_count=Count("bandecision"))
        .select_related("game__platform", "profile")
        .prefetch_related(
            Prefetch(
                "game__resultconfig_set",
                queryset=ResultConfig.objects.only("id", "has_points", "game_id"),
            )
        )
        .order_by("id")
    )


def get_full_standings_data(league: League) -> Dict:
    """Per-league entry point. Loads the five datasets and delegates the
    payload construction to ``build_full_standings_payload``."""
    members_list = list(
        league.members.select_related("profile__user").order_by(
            "rank", "profile__profile_name"
        )
    )
    required_bans = get_ban_amount_for_success(len(members_list))

    selected_games = list(
        _selected_games_qs({"league_id": league.id}).filter(ban_count__lt=required_bans)
    )
    league_standing_list = list(
        LeagueStanding.objects.filter(league_id=league.id).select_related(
            "player_profile__user"
        )
    )
    game_standings = list(
        GameStanding.objects.filter(league_id=league.id).select_related(
            "decisive_tie_breaker"
        )
    )
    tie_resolutions = list(
        LeagueTieResolution.objects.filter(league_id=league.id).prefetch_related(
            "entries__player_profile__user"
        )
    )

    return build_full_standings_payload(
        league=league,
        selected_games=selected_games,
        league_standing_list=league_standing_list,
        game_standings=game_standings,
        members=members_list,
        tie_resolutions=tie_resolutions,
    )


def build_full_standings_for_season(leagues: List[League]) -> List[Dict]:
    """Bulk-load every dataset once for all leagues in the season and build
    the per-league full-standings payload in Python.

    This is the constant-query backend for ``GET /seasons/{id}/full-standings/``
    used by the season-standings page on the frontend, replacing the previous
    ``1 + N`` HTTP round-trips and ``O(N)`` SQL fan-out.
    """
    if not leagues:
        return []

    league_ids = [l.id for l in leagues]

    # ---- one bulk query per dataset, grouped by league_id in Python --------
    selected_games_by_league: Dict[int, List] = {lid: [] for lid in league_ids}
    for sg in _selected_games_qs({"league_id__in": league_ids}):
        selected_games_by_league.setdefault(sg.league_id, []).append(sg)

    members_by_league: Dict[int, List] = {lid: [] for lid in league_ids}
    members_qs = (
        SeasonParticipant.objects.filter(leagues_member__in=league_ids)
        .select_related("profile__user")
        .prefetch_related("leagues_member")
    )
    for m in members_qs:
        # A participant can belong to multiple leagues (theoretically), so
        # bucket them by every league in ``league_ids`` they're a member of.
        for lg in m.leagues_member.all():
            if lg.id in members_by_league:
                members_by_league[lg.id].append(m)
    # Stable per-league ordering: rank, then profile_name
    for lid, lst in members_by_league.items():
        lst.sort(
            key=lambda m: (
                m.rank if m.rank is not None else 10**9,
                (m.profile.profile_name or ""),
            )
        )

    league_standings_by_league: Dict[int, List] = {lid: [] for lid in league_ids}
    for ls in LeagueStanding.objects.filter(league_id__in=league_ids).select_related(
        "player_profile__user"
    ):
        league_standings_by_league.setdefault(ls.league_id, []).append(ls)

    game_standings_by_league: Dict[int, List] = {lid: [] for lid in league_ids}
    for gs in GameStanding.objects.filter(league_id__in=league_ids).select_related(
        "decisive_tie_breaker"
    ):
        game_standings_by_league.setdefault(gs.league_id, []).append(gs)

    tie_resolutions_by_league: Dict[int, List] = {lid: [] for lid in league_ids}
    for tr in LeagueTieResolution.objects.filter(
        league_id__in=league_ids
    ).prefetch_related("entries__player_profile__user"):
        tie_resolutions_by_league.setdefault(tr.league_id, []).append(tr)

    # ---- per-league payload (filter selected_games by ban threshold) -------
    payloads: List[Dict] = []
    for league in leagues:
        members_for_league = members_by_league.get(league.id, [])
        required_bans = get_ban_amount_for_success(len(members_for_league))
        sgs = [
            sg
            for sg in selected_games_by_league.get(league.id, [])
            if sg.ban_count < required_bans
        ]
        payload = build_full_standings_payload(
            league=league,
            selected_games=sgs,
            league_standing_list=league_standings_by_league.get(league.id, []),
            game_standings=game_standings_by_league.get(league.id, []),
            members=members_for_league,
            tie_resolutions=tie_resolutions_by_league.get(league.id, []),
        )
        payload.update({"id": league.id, "level": league.level, "name": str(league)})
        payloads.append(payload)

    return payloads


def set_league_active_player(league: League, participant) -> None:
    from django.utils import timezone
    league.active_player = participant
    league.updated_at = timezone.now()
    league.save(update_fields=["active_player", "updated_at"])


def touch_league(league: League) -> None:
    from django.utils import timezone
    league.updated_at = timezone.now()
    league.save(update_fields=["updated_at"])


def rotate_active_player(
    league: League, reverse_order: bool = False, members=None
) -> Optional[SeasonParticipant]:
    players = members if members is not None else league.members.all()
    ordered_players = list(players.order_by("-rank" if reverse_order else "rank"))
    if not ordered_players:
        return None

    current = league.active_player
    if current not in ordered_players:
        next_player = ordered_players[0]
    else:
        i = ordered_players.index(current)
        next_player = ordered_players[(i + 1) % len(ordered_players)]

    from django.utils import timezone
    league.active_player = next_player
    league.updated_at = timezone.now()
    league.save(update_fields=["active_player", "updated_at"])
    return next_player


@transaction.atomic
def advance_turn(league: League):
    if league.status == LeagueStatus.PICKING:
        if q.all_players_have_picked(league):
            from django.utils import timezone
            league.status = LeagueStatus.BANNING
            league.active_player = q.get_members_ordered(league).first()
            league.updated_at = timezone.now()
            league.save(update_fields=["status", "active_player", "updated_at"])
        else:
            if q.is_two_player_league(league):
                if q.both_players_exactly_one_pick(league):
                    return
            rotate_active_player(league)

    elif league.status == LeagueStatus.REPICKING:
        if q.all_repickers_have_repicked(league):
            from django.utils import timezone
            league.status = LeagueStatus.PLAYING
            league.active_player = None
            league.updated_at = timezone.now()
            league.save(update_fields=["status", "active_player", "updated_at"])
        else:
            players_to_repick = q.get_players_to_repick(league)
            # rotate_active_player expects a queryset (uses order_by),
            # so convert the returned list of members to a queryset
            qs = league.members.filter(id__in=[m.id for m in players_to_repick])
            rotate_active_player(league, members=qs)

    elif league.status == LeagueStatus.BANNING:
        if q.all_players_have_banned(league):
            players_to_repick = q.get_players_to_repick(league)
            from django.utils import timezone
            if players_to_repick:
                league.status = LeagueStatus.REPICKING
                league.updated_at = timezone.now()
                league.save(update_fields=["status", "updated_at"])
                qs = league.members.filter(id__in=[m.id for m in players_to_repick])
                rotate_active_player(league, members=qs)
            else:
                league.status = LeagueStatus.PLAYING
                league.active_player = None
                league.updated_at = timezone.now()
                league.save(update_fields=["status", "active_player", "updated_at"])
        else:
            rotate_active_player(league)

    # PLAYING/DONE → do nothing


def select_game(league: League, player, game):
    if league.active_player != player:
        raise ValueError("It's not this player's turn to select a game.")
    selected = SelectedGame.objects.create(league=league, player=player, game=game)
    touch_league(league)
    return selected


def ban_game(league: League, player, game):
    if league.active_player != player:
        raise ValueError("It's not this player's turn to ban a game.")
    ban = BanDecision.objects.create(league=league, player=player, game=game)
    touch_league(league)
    return ban
