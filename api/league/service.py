def get_active_player(league):
    """
    Get the currently active player for the given league.
    """
    return league.active_player


def get_league_members_order(league):
    # Use the related name to access members and order them by rank
    members = league.members.all().order_by('rank')
    return members


def next_player(league):
    """
    Rotate to the next player in the league based on the defined order and set as active player.
    """
    # Get the ordered members as a list
    members = list(get_league_members_order(league))

    # Check if there are no members in the league
    if not members:
        return None  # No members in the league

    # Handle the case where there is no active player set
    active_player = league.active_player
    if active_player not in members:
        active_player_index = -1  # Start before the first player
    else:
        active_player_index = members.index(active_player)

    # Rotate to the next player
    next_player_index = (active_player_index + 1) % len(members)
    next_player = members[next_player_index]

    # Update the active player in the league
    league.active_player = next_player
    league.save()

    return next_player  # Return the new active player


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
