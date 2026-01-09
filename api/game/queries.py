from typing import Optional, List
from django.db.models import QuerySet, Count
from game.models import Game, SelectedGame, BanDecision, Faction, TieBreaker, ResultConfig
from league.models import League
from api.constants import get_ban_amount_for_success

def get_all_games() -> QuerySet:
    return Game.objects.all()

def get_game_by_id(game_id: int) -> Optional[Game]:
    return Game.objects.filter(id=game_id).first()

def get_selected_games_for_league(league: League) -> QuerySet:
    return SelectedGame.objects.filter(league=league)

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
    
    return list(BanDecision.objects.filter(league=league, selected_game__isnull=False)
        .values("selected_game_id")
        .annotate(c=Count("id"))
        .filter(c__gte=min_bans)
        .values_list("selected_game_id", flat=True))

def get_factions_for_game(game: Game) -> QuerySet:
    return Faction.objects.filter(game=game)

def get_tie_breakers_for_config(result_config: ResultConfig) -> QuerySet:
    return TieBreaker.objects.filter(result_config=result_config).order_by('order')

def get_result_config_for_game(game: Game) -> Optional[ResultConfig]:
    return ResultConfig.objects.filter(game=game).first()
