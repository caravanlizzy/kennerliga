from typing import List
from league.models import League
from game.models import SelectedGame, BanDecision


def get_members_ordered(league: League):
    """Return league members ordered by rank."""
    return league.members.all().select_related("profile").order_by("rank")


def all_players_have_picked(league: League) -> bool:
    """Check if all league members have selected a game."""
    expected_count = 2 if is_two_player_league(league) else 1
    for participant in league.members.all():
        pick_count = SelectedGame.objects.filter(
            league=league,
            profile=participant.profile
        ).count()
        if pick_count < expected_count:
            return False
    return True


def all_players_have_banned(league: League) -> bool:
    """Check if all league members have submitted at least one ban."""
    expected_ban_count = 1

    for participant in league.members.all():
        ban_count = BanDecision.objects.filter(
            league=league,
            player_banning=participant.profile
        ).count()
        if ban_count < expected_ban_count:
            return False
    return True


def get_players_to_repick(league: League) -> List:
    """Return members who must repick because at least one of their games was banned."""
    from django.db.models import Count  # local import to keep file-level imports minimal

    repick_players = []
    min_bans = 2 if league.members.count() > 2 else 1

    for member in league.members.all():
        qs = SelectedGame.objects.filter(profile=member.profile, league=league)
        sgs = list(qs.only("id")[:2])  # in 2-player leagues, a player can have 2 picks

        if not sgs:
            continue

        # Count bans per selected game for this member (in this league)
        banned_counts = (
            BanDecision.objects.filter(league=league, selected_game__in=sgs)
            .values("selected_game_id")
            .annotate(c=Count("id"))
        )

        if any(row["c"] >= min_bans for row in banned_counts):
            repick_players.append(member)

    return repick_players


def all_repickers_have_repicked(league: League) -> bool:
    expected_count = 3 if is_two_player_league(league) else 2
    """Check if all players who must repick have done so."""
    for player in get_players_to_repick(league):
        # For 2-player leagues, players should have 3 games if they had to repick
        # For other leagues, they should have more than 1 game
        actual_count = SelectedGame.objects.filter(
            profile=player.profile,
            league=league
        ).count()
        if actual_count < expected_count:
            return False
    return True


def is_two_player_league(league: League) -> bool:
    return league.members.count() == 2

def both_players_exactly_one_pick(league: League) -> bool:
    return SelectedGame.objects.filter(league=league).count() == 2