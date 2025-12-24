from typing import Optional
from django.db import transaction
from game.models import SelectedGame, BanDecision
from league.models import League, LeagueStatus
from season.models import SeasonParticipant
from league import queries as q


class LeagueService:
    def __init__(self, league: League):
        self.league = league

    def rotate_active_player(self, reverse_order: bool = False, members=None) -> Optional[SeasonParticipant]:
        players = members if members is not None else self.league.members.all()
        ordered_players = list(players.order_by("-rank" if reverse_order else "rank"))
        if not ordered_players:
            return None

        current = self.league.active_player
        if current not in ordered_players:
            next_player = ordered_players[0]
        else:
            i = ordered_players.index(current)
            next_player = ordered_players[(i + 1) % len(ordered_players)]

        self.league.active_player = next_player
        self.league.save(update_fields=["active_player"])
        return next_player

    @transaction.atomic
    def advance_turn(self):
        if self.league.status == LeagueStatus.PICKING:
            if q.all_players_have_picked(self.league):
                self.league.status = LeagueStatus.BANNING
                self.league.active_player = q.get_members_ordered(self.league).first()
                self.league.save(update_fields=["status", "active_player"])
            else:
                if q.is_two_player_league(self.league):
                    if q.both_players_exactly_one_pick(self.league):
                        return
                self.rotate_active_player()

        elif self.league.status == LeagueStatus.REPICKING:
            if q.all_repickers_have_repicked(self.league):
                self.league.status = LeagueStatus.PLAYING
                self.league.active_player = None
                self.league.save(update_fields=["status", "active_player"])
            else:
                self.rotate_active_player()

        elif self.league.status == LeagueStatus.BANNING:
            if q.all_players_have_banned(self.league):
                players_to_repick = q.get_players_to_repick(self.league)
                if players_to_repick:
                    self.league.status = LeagueStatus.REPICKING
                    self.league.save(update_fields=["status"])
                    qs = self.league.members.filter(id__in=[m.id for m in players_to_repick])
                    self.rotate_active_player(members=qs)
                else:
                    self.league.status = LeagueStatus.PLAYING
                    self.league.active_player = None
                    self.league.save(update_fields=["status", "active_player"])
            else:
                self.rotate_active_player()

        # PLAYING/DONE → do nothing

    def select_game(self, player, game):
        if self.league.active_player != player:
            raise ValueError("It's not this player's turn to select a game.")
        return SelectedGame.objects.create(league=self.league, player=player, game=game)

    def ban_game(self, player, game):
        if self.league.active_player != player:
            raise ValueError("It's not this player's turn to ban a game.")
        return BanDecision.objects.create(league=self.league, player=player, game=game)
