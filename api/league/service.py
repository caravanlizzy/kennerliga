from game.models import SelectedGame


def get_active_player(league):
    """
    Get the currently active player for the given league.
    """
    return league.active_player


def get_league_members_order(league):
    # Use the related name to access members and order them by rank
    members = league.members.all().order_by('rank')
    return members


def rotate_active_player(league, reverse_order=False):
    """
    Rotate to the next player in the league and update the active player.
    Players are ordered by rank unless reverse_order is True.
    """
    ordered_players = list(get_league_members_order(league))
    if reverse_order:
        ordered_players = ordered_players[::-1]

    if not ordered_players:
        return None  # No players in the league

    current_player = league.active_player
    if current_player not in ordered_players:
        current_index = -1  # Start before the first player
    else:
        current_index = ordered_players.index(current_player)

    next_index = (current_index + 1) % len(ordered_players)
    next_player = ordered_players[next_index]

    league.active_player = next_player
    league.save()

    return next_player



def have_all_players_picked(league):
    """
    Check if all players in the league have picked a game.
    """
    members = league.members.all()
    for member in members:
        if not SelectedGame.objects.filter(league=league, player=member.profile).exists():
            return False
    return True


def advance_league_turn(league):
    from league.models import LeagueStatus

    if league.status == LeagueStatus.PICKING:
        if have_all_players_picked(league):
            league.status = LeagueStatus.BANNING
            league.save()
        else:
            rotate_active_player(league)

    elif league.status == LeagueStatus.BANNING:
        if have_all_players_banned(league):
            league.status = LeagueStatus.PLAYING
            league.active_player = None
            league.save()
        else:
            rotate_active_player(league, reverse_order=True)

    else:
        print("No more rotation required since LeagueStatus is PLAYING or DONE. Current LeagueStatus: " + league.status)



def select_game(league, player, game):
    """
    Simulate a player selecting a game for the league.
    Args:
        league: The league instance.
        player: The player selecting the game.
        game: The game being selected.
    """
    if league.active_player != player:
        raise ValueError("It's not this player's turn to select a game.")

    # Perform logic to mark the game as selected for the league
    # Example: Add to a selected games table or update the league state
    # Integrate with a Game model as necessary
    return f"Player {player} selected game {game} for League {league}."


def ban_game(league, player, game):
    """
    Simulate a player banning a game for the league.
    Args:
        league: The league instance.
        player: The player banning the game.
        game: The game being banned.
    """
    if league.active_player != player:
        raise ValueError("It's not this player's turn to ban a game.")

    # Perform logic to mark the game as banned for the league
    # Example: Add to a banned games table or update the league state
    # Integrate with a Game model as necessary
    return f"Player {player} banned game {game} for League {league}."