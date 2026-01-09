from typing import Optional, List
from django.db.models import QuerySet
from result.models import Result
from league.models import League
from season.models import Season

def get_results_for_league(league: League) -> QuerySet:
    return Result.objects.filter(league=league)

def get_results_for_season(season: Season) -> QuerySet:
    return Result.objects.filter(season=season)

def get_results_for_selected_game(selected_game) -> QuerySet:
    return Result.objects.filter(selected_game=selected_game)

def get_result_by_id(result_id: int) -> Optional[Result]:
    return Result.objects.filter(id=result_id).first()
