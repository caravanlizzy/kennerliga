from collections import Counter
from typing import Optional, List
from django.db.models import QuerySet, Count
from game.models import (
    Game,
    SelectedGame,
    BanDecision,
    Faction,
    ResultConfig,
)
from league.models import League
from api.constants import get_ban_amount_for_success
from configuration.services import get_max_same_game_per_year


def get_all_games(selectable_only=True) -> QuerySet:
    """
    Returns a queryset of all games, optionally filtering by selectable status.
    """
    if selectable_only:
        return Game.objects.filter(selectable=True)
    return Game.objects.all()


def get_game_by_id(game_id: int) -> Optional[Game]:
    """
    Retrieves a game by its ID.
    """
    return Game.objects.filter(id=game_id).first()


def get_related_game_ids(game: Game) -> set[int]:
    """
    Returns a set of IDs for games related to the given game.
    """
    return set(game.related_games.values_list("id", flat=True))


def get_game_ids_including_related(game_ids) -> set[int]:
    """
    Given a list of game IDs, returns a set including those IDs and all their related game IDs.
    """
    game_ids = set(game_ids)

    related_game_ids = Game.objects.filter(id__in=game_ids).values_list(
        "related_games__id", flat=True
    )

    return game_ids | {game_id for game_id in related_game_ids if game_id is not None}


def get_selected_games_for_league(league: League) -> QuerySet:
    """
    Returns a queryset of SelectedGame objects for a specific league.
    """
    return SelectedGame.objects.filter(league=league)


def get_selected_game_ids_for_league_including_related(league: League) -> set[int]:
    """
    Returns a set of all game IDs (including related ones) already selected for the given league.
    """
    selected_game_ids = get_selected_games_for_league(league).values_list(
        "game_id", flat=True
    )
    return get_game_ids_including_related(selected_game_ids)


def get_max_selected_game_ids_for_profile_in_year_including_related(
    profile,
    season,
    excluded_selected_game_id: Optional[int] = None,
) -> set[int]:
    """
    Returns a set of game IDs that the player has already selected the maximum number of times in the given season's year.
    Includes related games in the count.
    """
    selected_games = (
        SelectedGame.objects.filter(
            profile=profile,
            league__season__year=season.year,
        )
        .select_related("game")
        .prefetch_related("game__related_games")
    )

    successfully_banned_selected_game_ids = get_successfully_banned_game_ids(
        year=season.year
    )
    selected_games = selected_games.exclude(
        id__in=successfully_banned_selected_game_ids
    )

    if excluded_selected_game_id:
        selected_games = selected_games.exclude(id=excluded_selected_game_id)

    selection_counts = Counter()

    for selected_game in selected_games:
        counted_game_ids = {
            selected_game.game_id,
            *selected_game.game.related_games.values_list("id", flat=True),
        }

        for game_id in counted_game_ids:
            selection_counts[game_id] += 1

    max_same_game_per_year = get_max_same_game_per_year()
    return {
        game_id
        for game_id, count in selection_counts.items()
        if count >= max_same_game_per_year
    }


def get_selected_game_by_id(sg_id: int) -> Optional[SelectedGame]:
    """
    Retrieves a SelectedGame by its ID.
    """
    return SelectedGame.objects.filter(id=sg_id).first()


def get_ban_decisions_for_league(league: League) -> QuerySet:
    """
    Returns a queryset of BanDecision objects for a specific league.
    """
    return BanDecision.objects.filter(league=league)


def is_game_successfully_banned(selected_game: SelectedGame) -> bool:
    """
    Checks if a selected game has been successfully banned based on the league's ban requirements.
    """
    league = selected_game.league
    if not league:
        return False

    required_bans = get_ban_amount_for_success(league.members.count())
    ban_count = BanDecision.objects.filter(selected_game=selected_game).count()
    return ban_count >= required_bans


def get_banned_selected_game_ids(league: League) -> List[int]:
    """
    Returns a list of IDs for SelectedGames that have been successfully banned in the given league.
    """
    required_bans = get_ban_amount_for_success(league.members.count())

    return list(
        BanDecision.objects.filter(league=league, selected_game__isnull=False)
        .values("selected_game_id")
        .annotate(c=Count("id"))
        .filter(c__gte=required_bans)
        .values_list("selected_game_id", flat=True)
    )


def get_successfully_banned_game_ids(year: int = None) -> List[int]:
    """
    Returns a list of SelectedGame IDs that were successfully banned.
    A game is successfully banned if the number of BanDecisions for it
    reaches the required threshold for its league.
    """
    qs = BanDecision.objects.filter(selected_game__isnull=False)
    if year:
        qs = qs.filter(league__season__year=year)

    selected_games = SelectedGame.objects.filter(id__in=qs.values("selected_game_id"))
    if year:
        selected_games = selected_games.filter(league__season__year=year)

    # The ban threshold depends on the league's member count, so load the
    # member count for every league involved in one grouped query over the
    # M2M through table instead of calling ``league.members.count()`` per
    # SelectedGame.
    rows = list(selected_games.annotate(ban_count=Count("bandecision")).values_list(
        "id", "league_id", "ban_count"
    ))
    member_counts = {
        row["league_id"]: row["c"]
        for row in League.members.through.objects.filter(
            league_id__in={league_id for _, league_id, _ in rows}
        )
        .values("league_id")
        .annotate(c=Count("id"))
    }

    return [
        sg_id
        for sg_id, league_id, ban_count in rows
        if ban_count >= get_ban_amount_for_success(member_counts.get(league_id, 0))
    ]


def get_factions_for_game(game: Game) -> QuerySet:
    """
    Returns a queryset of Faction objects for a specific game.
    """
    return Faction.objects.filter(game=game)


def get_result_config_for_game(game: Game) -> Optional[ResultConfig]:
    """
    Retrieves the ResultConfig for a specific game.
    """
    return ResultConfig.objects.filter(game=game).first()
