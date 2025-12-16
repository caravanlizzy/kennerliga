from typing import List
from league.models import League
from game.models import SelectedGame, BanDecision


def get_members_ordered(league: League):
    """Return league members ordered by rank."""
    return league.members.all().select_related("profile").order_by("rank")


def all_players_have_banned(league: League) -> bool:
    """Check if all league members have submitted at least one ban."""
    two_player_league = is_two_player_league(league)
    expected_count = 1 if two_player_league else 2

    for participant in league.members.all():
        ban_count = BanDecision.objects.filter(
            league=league,
            player_banning=participant.profile
        ).count()
        if ban_count < expected_count:
            return False
    return True


def get_players_to_repick(league: League) -> List:
    """Return members who must repick because their only game was banned."""
    repick_players = []
    min_bans = 2 if league.members.count() > 2 else 1

    for member in league.members.all():
        qs = SelectedGame.objects.filter(profile=member.profile, league=league)
        sgs = list(qs.only('id')[:2])           # 1 query, avoids count()+first() double hit
        if len(sgs) == 1:
            sg = sgs[0]
            ban_count = BanDecision.objects.filter(
                league=league,
                selected_game=sg               # or: selected_game_id=sg.id
            ).count()
            if ban_count >= min_bans:
                repick_players.append(member)
    return repick_players


def all_repickers_have_repicked(league: League) -> bool:
    expected_count = 3 if is_two_player_league(league) else 2
    """Check if all players who must repick have done so."""
    for player in get_players_to_repick(league):
        # For 2-player leagues, players should have 3 games if they had to repick
        # For other leagues, they should have more than 1 game
        actual_count = SelectedGame.objects.filter(
            player=player.profile,
            league=league
        ).count()
        if actual_count < expected_count:
            return False
    return True

def is_two_player_league(league: League) -> bool:
    return league.members.count() == 2