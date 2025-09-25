from typing import List
from league.models import League
from game.models import SelectedGame, BanDecision


def get_members_ordered(league: League):
    """Return league members ordered by rank."""
    return league.members.all().select_related("profile").order_by("rank")


def all_players_have_picked(league: League) -> bool:
    """Check if all league members have selected a game."""
    for participant in league.members.all():
        if not SelectedGame.objects.filter(league=league, player=participant.profile).exists():
            return False
    return True


def all_players_have_banned(league: League) -> bool:
    """Check if all league members have submitted at least one ban."""
    for participant in league.members.all():
        if not BanDecision.objects.filter(league=league, player_banning=participant.profile).exists():
            return False
    return True


def get_players_to_repick(league: League) -> List:
    """Return members who must repick because their only game was banned."""
    repick_players = []
    min_bans = 2 if league.members.count() > 2 else 1

    for member in league.members.all():
        qs = SelectedGame.objects.filter(player=member.profile, league=league)
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
    """Check if all players who must repick have done so."""
    for player in get_players_to_repick(league):
        if not SelectedGame.objects.filter(player=player.profile, league=league).count() > 1:
            return False
    return True