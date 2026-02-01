from typing import Optional, List, Dict
from django.db import transaction
from django.db.models import Count
from game.models import SelectedGame, BanDecision
from league.models import League, LeagueStatus, LeagueStanding, GameStanding
from season.models import SeasonParticipant
from league import queries as q
from api.constants import get_ban_amount_for_success

def get_full_standings_data(league: League) -> Dict:
    required_bans = get_ban_amount_for_success(league.members.count())

    # 1. Get all selected games for this league (column headers)
    selected_games = (
        SelectedGame.objects
        .filter(league=league)
        .annotate(ban_count=Count('bandecision'))
        .filter(ban_count__lt=required_bans)
        .select_related('game__platform', 'profile')
        .prefetch_related('game__resultconfig_set')
        .order_by('id')
    )
    
    selected_game_list = []
    for sg in selected_games:
        configs = list(sg.game.resultconfig_set.all())
        selected_game_list.append({
            "id": sg.id,
            "game_name": sg.game.name,
            "game_short_name": sg.game.short_name,
            "platform_name": sg.game.platform.name,
            "has_points": configs[0].has_points if configs else True,
            "selected_by_id": sg.profile.id if sg.profile else None,
            "selected_by_name": sg.profile.profile_name if sg.profile else None,
        })
    selected_game_ids = [sg.id for sg in selected_games]

    # 2. Get league standings (for row ordering & totals)
    league_standings = (
        LeagueStanding.objects
        .filter(league=league)
        .select_related('player_profile__user')
    )
    league_standing_dict = {ls.player_profile_id: ls for ls in league_standings}

    # 3. Get all game standings for this league
    game_standings = (
        GameStanding.objects
        .filter(league=league)
        .select_related('decisive_tie_breaker')
    )

    # Build a lookup: {player_profile_id: {selected_game_id: {...}}}
    game_data_by_player = {}
    for gs in game_standings:
        pid = gs.player_profile_id
        if pid not in game_data_by_player:
            game_data_by_player[pid] = {}
        game_data_by_player[pid][gs.selected_game_id] = {
            "points": str(gs.points),
            "league_points": str(gs.league_points),
            "rank": gs.rank,
            "decisive_tie_breaker_name": gs.decisive_tie_breaker.name if gs.decisive_tie_breaker else None,
            "tie_breaker_value": gs.tie_breaker_value,
        }

    # 4. Get all members of the league to ensure everyone is listed even if they have no standings yet
    members = (
        league.members
        .select_related('profile__user')
        .order_by('rank', 'profile__profile_name')
    )

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
                games_dict[str(sg_id)] = {"points": None, "league_points": None, "rank": None}

        standings_list.append({
            "player_profile_id": pid,
            "profile_name": member.profile.profile_name,
            "user_id": member.profile.user.id if member.profile.user else None,
            "username": member.profile.user.username if member.profile.user else None,
            "total_league_points": str(ls.league_points) if ls else "0",
            "total_wins": str(ls.wins) if ls else "0",
            "games": games_dict,
        })

    # Sort standings_list: if we have LeagueStandings, sort by them, otherwise stick to member rank
    if league_standings.exists():
        standings_list.sort(key=lambda x: (
            -float(x["total_league_points"]),
            -float(x["total_wins"]),
            x["profile_name"]
        ))

    return {
        "selected_games": selected_game_list,
        "standings": standings_list,
        "season_id": league.season_id
    }

def rotate_active_player(league: League, reverse_order: bool = False, members=None) -> Optional[SeasonParticipant]:
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

    league.active_player = next_player
    league.save(update_fields=["active_player"])
    return next_player

@transaction.atomic
def advance_turn(league: League):
    if league.status == LeagueStatus.PICKING:
        if q.all_players_have_picked(league):
            league.status = LeagueStatus.BANNING
            league.active_player = q.get_members_ordered(league).first()
            league.save(update_fields=["status", "active_player"])
        else:
            if q.is_two_player_league(league):
                if q.both_players_exactly_one_pick(league):
                    return
            rotate_active_player(league)

    elif league.status == LeagueStatus.REPICKING:
        if q.all_repickers_have_repicked(league):
            league.status = LeagueStatus.PLAYING
            league.active_player = None
            league.save(update_fields=["status", "active_player"])
        else:
            rotate_active_player(league)

    elif league.status == LeagueStatus.BANNING:
        if q.all_players_have_banned(league):
            players_to_repick = q.get_players_to_repick(league)
            if players_to_repick:
                league.status = LeagueStatus.REPICKING
                league.save(update_fields=["status"])
                qs = league.members.filter(id__in=[m.id for m in players_to_repick])
                rotate_active_player(league, members=qs)
            else:
                league.status = LeagueStatus.PLAYING
                league.active_player = None
                league.save(update_fields=["status", "active_player"])
        else:
            rotate_active_player(league)

    # PLAYING/DONE → do nothing

def select_game(league: League, player, game):
    if league.active_player != player:
        raise ValueError("It's not this player's turn to select a game.")
    return SelectedGame.objects.create(league=league, player=player, game=game)

def ban_game(league: League, player, game):
    if league.active_player != player:
        raise ValueError("It's not this player's turn to ban a game.")
    return BanDecision.objects.create(league=league, player=player, game=game)
