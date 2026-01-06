from decimal import Decimal

# League points distribution based on player count
# 4 player: 6, 3, 1, 0
# 3 players: 6, 3, 0
# 2 players: 6, 0
LEAGUE_POINTS_DISTRIBUTION = {
    4: {1: Decimal("6"), 2: Decimal("3"), 3: Decimal("1"), 4: Decimal("0")},
    3: {1: Decimal("6"), 2: Decimal("3"), 3: Decimal("0")},
    2: {1: Decimal("6"), 2: Decimal("0")},
}

# the number the same game can be picked within a year
MAX_SAME_GAME_PER_YEAR = 2

DEFAULT_LEAGUE_POINTS = {
    1: Decimal("6"),
    2: Decimal("3"),
    3: Decimal("1"),
    4: Decimal("0"),
}

def get_league_points(player_count: int) -> dict[int, Decimal]:
    return LEAGUE_POINTS_DISTRIBUTION.get(player_count, DEFAULT_LEAGUE_POINTS)

# Game picks per player
# 2 players: 2 per player
# 3+ player: 1 per player
def get_game_picks_per_player(player_count: int) -> int:
    if player_count == 2:
        return 2
    return 1


# Amount of BanDecisions required for a successful ban
def get_ban_amount_for_success(player_count: int) -> int:
    if player_count == 2:
        return 1
    return 2
