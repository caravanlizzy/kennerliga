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
        .select_related('game', 'profile')
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
        .order_by('-league_points', '-wins', 'player_profile__profile_name')
    )

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

    # 4. Build the response rows
    standings_list = []
    for ls in league_standings:
        pid = ls.player_profile_id
        player_games = game_data_by_player.get(pid, {})

        games_dict = {}
        for sg_id in selected_game_ids:
            if sg_id in player_games:
                games_dict[str(sg_id)] = player_games[sg_id]
            else:
                games_dict[str(sg_id)] = {"points": None, "league_points": None, "rank": None}

        standings_list.append({
            "player_profile_id": pid,
            "profile_name": ls.player_profile.profile_name,
            "user_id": ls.player_profile.user.id if ls.player_profile.user else None,
            "username": ls.player_profile.user.username if ls.player_profile.user else None,
            "total_league_points": str(ls.league_points),
            "total_wins": str(ls.wins),
            "games": games_dict,
        })

    return {
        "selected_games": selected_game_list,
        "standings": standings_list
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
