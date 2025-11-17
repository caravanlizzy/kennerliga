from __future__ import annotations

from decimal import Decimal
from django.db import transaction
from result.models import Result
from services.scoring import Row, compute_game_breakdown, compute_league_table
from league.models import LeagueStanding, GameStanding, League
from game.models import SelectedGame

@transaction.atomic
def rebuild_game_snapshot(selected_game: SelectedGame, *, win_mode: str = "count_top_block"):
    league = selected_game.league
    # pull raw results for this game
    qs = (
        Result.objects
        .filter(selected_game=selected_game.id)
        .select_related("player_profile")
        .only("selected_game_id", "player_profile", "player_profile__profile_name", "points")
    )
    rows = [
        Row(
            selected_game_id=selected_game.id,
            player_id=r.player_profile,
            player_name=r.player_profile.profile_name,
            points=Decimal(r.points),
        )
        for r in qs
    ]
    breakdown = compute_game_breakdown(rows, win_mode=win_mode, return_decimals=True)

    # upsert GameStanding rows for this selected_game
    existing = {
        (gs.player_profile): gs
        for gs in GameStanding.objects.filter(selected_game=selected_game.id)
    }
    to_create, to_update = [], []
    for r in breakdown:
        obj = existing.get(r["player_id"])
        if obj is None:
            to_create.append(GameStanding(
                league=league,
                selected_game=selected_game,
                player_profile=r["player_id"],
                points=r["points"],
                rank=r["rank"],
                league_points=r["league_points"],
                win_share=r["wins"],
            ))
        else:
            obj.points = r["points"]
            obj.rank = int(r["rank"])
            obj.league_points = r["league_points"]
            obj.win_share = r["wins"]
            to_update.append(obj)

    if to_create:
        GameStanding.objects.bulk_create(to_create)
    if to_update:
        GameStanding.objects.bulk_update(to_update, ["points", "rank", "league_points", "win_share"])


@transaction.atomic
def rebuild_league_snapshot(league: League, *, win_mode: str = "count_top_block"):
    # compute over all results in league
    qs = (
        Result.objects
        .filter(league=league)
        .select_related("selected_game", "player_profile")
        .only("selected_game_id", "player_profile", "player_profile__profile_name", "points")
    )
    rows = [
        Row(
            selected_game_id=r.selected_game_id,
            player_id=r.player_profile,
            player_name=r.player_profile.profile_name,
            points=Decimal(r.points),
        )
        for r in qs
    ]
    table = compute_league_table(rows, win_mode=win_mode, return_decimals=True)

    # upsert LeagueStanding (NO raw points)
    existing = {ls.player_profile: ls for ls in LeagueStanding.objects.filter(league=league)}
    to_create, to_update = [], []
    for r in table:
        obj = existing.get(r["player_id"])
        if obj is None:
            to_create.append(LeagueStanding(
                league=league,
                player_profile=r["player_id"],
                wins=r["wins"],
                league_points=r["league_points"],
            ))
        else:
            obj.wins = r["wins"]
            obj.league_points = r["league_points"]
            to_update.append(obj)

    if to_create:
        LeagueStanding.objects.bulk_create(to_create)
    if to_update:
        LeagueStanding.objects.bulk_update(to_update, ["wins", "league_points"])
