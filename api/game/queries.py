from collections import Counter
from typing import Optional, List
from django.db.models import QuerySet, Count
from game.models import (
    Game,
    SelectedGame,
    BanDecision,
    Faction,
    TieBreaker,
    ResultConfig,
)
from league.models import League
from api.constants import get_ban_amount_for_success, MAX_SAME_GAME_PER_YEAR


def get_all_games(selectable_only=True) -> QuerySet:
    if selectable_only:
        return Game.objects.filter(selectable=True)
    return Game.objects.all()


def get_game_by_id(game_id: int) -> Optional[Game]:
    return Game.objects.filter(id=game_id).first()


def get_related_game_ids(game: Game) -> set[int]:
    return set(game.related_games.values_list("id", flat=True))


def get_game_ids_including_related(game_ids) -> set[int]:
    game_ids = set(game_ids)

    related_game_ids = Game.objects.filter(id__in=game_ids).values_list(
        "related_games__id", flat=True
    )

    return game_ids | {game_id for game_id in related_game_ids if game_id is not None}


def get_selected_games_for_league(league: League) -> QuerySet:
    return SelectedGame.objects.filter(league=league)


def get_selected_game_ids_for_league_including_related(league: League) -> set[int]:
    selected_game_ids = get_selected_games_for_league(league).values_list(
        "game_id", flat=True
    )
    return get_game_ids_including_related(selected_game_ids)


def get_max_selected_game_ids_for_profile_in_year_including_related(
    profile,
    season,
    excluded_selected_game_id: Optional[int] = None,
) -> set[int]:
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

    return {
        game_id
        for game_id, count in selection_counts.items()
        if count >= MAX_SAME_GAME_PER_YEAR
    }


def get_selected_game_by_id(sg_id: int) -> Optional[SelectedGame]:
    return SelectedGame.objects.filter(id=sg_id).first()


def get_ban_decisions_for_league(league: League) -> QuerySet:
    return BanDecision.objects.filter(league=league)


def is_game_successfully_banned(selected_game: SelectedGame) -> bool:
    league = selected_game.league
    if not league:
        return False

    required_bans = get_ban_amount_for_success(league.members.count())
    ban_count = BanDecision.objects.filter(selected_game=selected_game).count()
    return ban_count >= required_bans


def get_banned_selected_game_ids(league: League) -> List[int]:
    member_count = league.members.count()
    min_bans = 2 if member_count > 2 else 1

    return list(
        BanDecision.objects.filter(league=league, selected_game__isnull=False)
        .values("selected_game_id")
        .annotate(c=Count("id"))
        .filter(c__gte=min_bans)
        .values_list("selected_game_id", flat=True)
    )


def get_successfully_banned_game_ids(year: int = None) -> List[int]:
    """
    Returns a list of SelectedGame IDs that were successfully banned.
    A game is successfully banned if the number of BanDecisions for it
    reaches the required threshold for its league.
    """
    from api.constants import get_ban_amount_for_success

    qs = BanDecision.objects.filter(selected_game__isnull=False)
    if year:
        qs = qs.filter(league__season__year=year)

    # We need to group by selected_game and check if count >= required_bans
    # Since required_bans depends on league member count, we need to handle it per league

    # Efficient way:
    # 1. Get all selected_game_ids and their ban counts for the given year
    # 2. Get the required ban count for each of those selected games
    # 3. Filter those that match

    ban_counts = qs.values(
        "selected_game_id", "selected_game__league__members"
    ).annotate(c=Count("id"))

    # Note: selected_game__league__members is a many-to-many, so this might duplicate rows
    # if not careful, but we just need the count of members.
    # Better:
    selected_games = SelectedGame.objects.filter(id__in=qs.values("selected_game_id"))
    if year:
        selected_games = selected_games.filter(league__season__year=year)

    successfully_banned_ids = []
    for sg in selected_games.annotate(ban_count=Count("bandecision")):
        member_count = sg.league.members.count()
        if sg.ban_count >= get_ban_amount_for_success(member_count):
            successfully_banned_ids.append(sg.id)

    return successfully_banned_ids


def get_factions_for_game(game: Game) -> QuerySet:
    return Faction.objects.filter(game=game)


def get_tie_breakers_for_config(result_config: ResultConfig) -> QuerySet:
    return TieBreaker.objects.filter(result_config=result_config).order_by("order")


def get_result_config_for_game(game: Game) -> Optional[ResultConfig]:
    return ResultConfig.objects.filter(game=game).first()
