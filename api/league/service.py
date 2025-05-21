from django.db import transaction
from django.db.models import Count, Q

from game.models import SelectedGame, BanDecision


def get_league_members_order(league):
    """
    Fetches and returns the league members ordered by their rank.

    This function retrieves all members of the given league and orders them
    based on their rank while also selecting related profile data to optimize
    database queries.

    Args:
        league: The league object whose members are to be retrieved.

    Returns:
        QuerySet: A Django QuerySet containing league members ordered by their rank.
    """
    return league.members.all().select_related('profile').order_by('rank')


def order_players_by_rank(players):
    """
    Sorts a list of players by their rank in ascending order.

    This function is designed to order the provided list or queryset of
    players based on their respective rank attribute. It assumes that
    the input supports an `order_by` method typical of Django querysets
    or similar data structures.

    Args:
        players (queryset): A collection of players to be sorted. The
            players must have a 'rank' attribute and the collection
            should support the `order_by()` method.

    Returns:
        queryset: A new collection of players sorted by their rank
            in ascending order.
    """
    return players.order_by('rank')


@transaction.atomic
def rotate_active_player(league, reverse_order=False, members=None):
    """
    Rotates the active player in a league based on their ranking and specified order.

    The function selects the next active player in a league by ordering players based
    on their rank, considering the active player and cycling through the list
    appropriately. The user can choose to reverse the order of player ranking. If
    no players are available or the league is invalid, the function will either
    raise an exception or return None.

    Args:
        league (League): The league object containing the active player and list
                         of members.
        reverse_order (bool, optional): Determines the ranking order. If set to
                                        True, players are ordered in descending
                                        rank. Defaults to False.
        members (QuerySet or None, optional): A specific list of members to consider
                                              instead of the league's full member
                                              list. Defaults to None.

    Returns:
        Player or None: The new active player if the operation is successful. Returns
                        None if there are no players in the league.

    Raises:
        ValueError: If the league parameter is None.
    """
    if not league:
        raise ValueError("League cannot be None")

    players = members if members is not None else league.members.all()
    order = '-rank' if reverse_order else 'rank'
    ordered_players = players.order_by(order)

    if not ordered_players.exists():
        return None

    current_player = league.active_player

    if current_player not in ordered_players:
        next_player = ordered_players.first()
    else:
        next_player = ordered_players.filter(
            rank__gt=current_player.rank
        ).first() or ordered_players.first()

    league.active_player = next_player
    league.save()

    return next_player


def all_players_have_picked(league):
    for participant in league.members.all():
        if not SelectedGame.objects.filter(league=league, player=participant.profile).exists():
            return False
    return True



def all_players_have_banned(league):
    """
    Determines if all players in a league have submitted a ban decision.

    Returns True if every member's profile has at least one BanDecision for the given league.
    """
    for participant in league.members.all():
        if not BanDecision.objects.filter(league=league, player=participant.profile).exists():
            return False
    return True



def get_players_to_repick(league):
    """
    Returns league members who:
    - Have exactly one SelectedGame in the league, and
    - That game was banned by a BanDecision.
    """
    repick_players = []

    for member in league.members.all():
        selected_games = SelectedGame.objects.filter(
            player=member.profile,
            league=league
        )

        if selected_games.count() == 1:
            selected_game = selected_games.first()

            was_banned = BanDecision.objects.filter(
                player=member.profile,
                league=league,
                banned_game=selected_game
            ).exists()

            if was_banned:
                repick_players.append(member)

    return repick_players



def advance_league_turn(league):
    """
    Advances the turn for a league by updating its status and active player based on the current
    progress of the league. Handles transitions between different statuses: PICKING, BANNING,
    REPICKING, PLAYING, or DONE.

    Parameters:
    league (League): The league object whose turn needs to be advanced.
    """
    from league.models import LeagueStatus

    if league.status == LeagueStatus.PICKING:
        if all_players_have_picked(league):
            league.status = LeagueStatus.BANNING
            ordered_players = get_league_members_order(league)
            league.active_player = ordered_players.last()
            league.save()
        else:
            rotate_active_player(league)

    elif league.status == LeagueStatus.BANNING:
        if all_players_have_banned(league):
            players_to_repick = get_players_to_repick(league)
            if players_to_repick:
                league.status = LeagueStatus.REPICKING
                rotate_active_player(league, reverse_order=False, members=players_to_repick)
                league.save()
            else:
                league.status = LeagueStatus.PLAYING
                league.active_player = None
                league.save()
        else:
            rotate_active_player(league, reverse_order=True)

    else:
        print("No more rotation required since LeagueStatus is PLAYING or DONE. Current LeagueStatus: " + league.status)


def select_game(league, player, game):
    """
    Selects a game for a player in a league who is currently active. This function ensures
    the correct player selects a game and records the selection in the database.

    Args:
        league (League): The league in which the player and game exist.
        player (Player): The player attempting to select the game.
        game (Game): The game being selected by the player.

    Raises:
        ValueError: If the provided player is not the currently active player in the league.

    Returns:
        SelectedGame: The newly created record of the game selection.
    """
    if league.active_player != player:
        raise ValueError("It's not this player's turn to select a game.")
    return SelectedGame.objects.create(league=league, player=player, game=game)


def ban_game(league, player, game):
    """
    Ban a game for a player in a given league context.

    This function creates a ban decision for a specific game and player within a league.
    The function assumes that only the active player in the league is allowed to perform
    the banning operation. A ValueError will be raised if a player attempts
    to ban a game when it is not their turn.

    Parameters:
    league: The league context in which the ban is being applied.
    player: The player who is performing the banning action.
    game: The game to be banned.

    Raises:
    ValueError: If the specified player is not the active player in the league.

    Returns:
    BanDecision: The record of the created game ban decision.
    """
    if league.active_player != player:
        raise ValueError("It's not this player's turn to ban a game.")
    return BanDecision.objects.create(league=league, player=player, banned_game=game)
