from django.db.models import Count
from typing import List
from league.models import League
from game.models import SelectedGame, BanDecision
from api.constants import get_game_picks_per_player


def get_members_ordered(league: League):
    """Return league members ordered by rank."""
    return league.members.all().select_related("profile").order_by("rank")


def all_players_have_picked(league: League) -> bool:
    """Check if all league members have selected a game."""
    members = league.members.all()
    member_count = members.count()
    expected_count = get_game_picks_per_player(member_count)
    
    pick_counts = SelectedGame.objects.filter(
        league=league
    ).values("profile").annotate(count=Count("id"))
    
    pick_counts_map = {item["profile"]: item["count"] for item in pick_counts}
    
    for participant in members:
        if pick_counts_map.get(participant.profile_id, 0) < expected_count:
            return False
    return True

def all_players_have_banned(league: League) -> bool:
    """Check if all league members have submitted at least one ban."""
    members = league.members.all()
    expected_ban_count = 1

    ban_counts = BanDecision.objects.filter(
        league=league
    ).values("player_banning").annotate(count=Count("id"))
    
    ban_counts_map = {item["player_banning"]: item["count"] for item in ban_counts}

    for participant in members:
        if ban_counts_map.get(participant.profile_id, 0) < expected_ban_count:
            return False
    return True


def get_players_to_repick(league: League) -> List:
    """Return members who must repick because at least one of their games was banned."""
    member_count = league.members.count()
    min_bans = 2 if member_count > 2 else 1

    # Get all banned game IDs for this league
    banned_game_ids = (
        BanDecision.objects.filter(league=league, selected_game__isnull=False)
        .values("selected_game_id")
        .annotate(c=Count("id"))
        .filter(c__gte=min_bans)
        .values_list("selected_game_id", flat=True)
    )

    # Find members who have at least one of these games as their pick
    repick_players = []
    for member in league.members.all().select_related("profile"):
        # We only care about the first 2 picks (per the original logic)
        has_banned_pick = SelectedGame.objects.filter(
            profile=member.profile, 
            league=league, 
            id__in=banned_game_ids
        ).exists()
        
        # Original logic had some slicing: sgs = list(qs.only("id")[:2])
        # If we want to be exact:
        if has_banned_pick:
            sgs_ids = list(SelectedGame.objects.filter(profile=member.profile, league=league).values_list("id", flat=True)[:2])
            if any(sg_id in banned_game_ids for sg_id in sgs_ids):
                repick_players.append(member)

    return repick_players


def all_repickers_have_repicked(league: League) -> bool:
    expected_count = get_game_picks_per_player(league.members.count()) + 1
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

def is_league_finished(league: League) -> bool:
    """Check if all expected games in the league have been played and have results."""
    member_count = league.members.count()
    if member_count == 0:
        return False

    # Expected games count
    picks_per_player = get_game_picks_per_player(member_count)
    expected_games_count = member_count * picks_per_player
    
    # Games that are not banned
    # Assuming there's no easy way to check if a game is NOT banned without checking BanDecision
    # Actually, a better way is to see if we have enough SelectedGames that have results.
    
    # Get all SelectedGames for this league
    selected_games = SelectedGame.objects.filter(league=league)
    
    # We need to filter out banned games. 
    # A game is banned if there is a BanDecision pointing to it.
    # Actually, it depends on min_bans.
    min_bans = 2 if member_count > 2 else 1
    
    from django.db.models import Count
    banned_game_ids = (
        BanDecision.objects.filter(league=league, selected_game__isnull=False)
        .values("selected_game_id")
        .annotate(c=Count("id"))
        .filter(c__gte=min_bans)
        .values_list("selected_game_id", flat=True)
    )
    
    active_games = selected_games.exclude(id__in=banned_game_ids)
    
    if active_games.count() < expected_games_count:
        # Not all games have been picked/repicked yet
        return False
        
    # Check if all active games have results
    from result.models import Result
    for game in active_games:
        result_count = Result.objects.filter(selected_game=game).count()
        if result_count < member_count:
            return False
            
    return True