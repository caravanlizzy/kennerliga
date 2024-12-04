def get_active_player(league):
    """
    Get the currently active player for the given league.
    """
    return league.active_player


def get_league_members_order(league):
    """
    get order based on season order
    """
    return


def next_player(league):
    """
    Rotate to the next player in the league based on the defined order and set as active player.
    """
    members = get_league_members_order(league)
    if not members:
        return None  # No members in the league

    # Find the index of the current active player
    if league.active_player in members:
        current_index = members.index(league.active_player)
        next_index = (current_index + 1) % len(members)  # Circular rotation
    else:
        next_index = 0  # Default to the first member if no active player

    # Update and save the active player
    league.active_player = members[next_index]
    league.save()

    return league.active_player


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
