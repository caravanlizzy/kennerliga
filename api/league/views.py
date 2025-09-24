from django.db.models import Prefetch
from django.db.models import prefetch_related_objects
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet

from game.models import SelectedGame, BanDecision
from league.models import League
from league.serializer import LeagueSerializer, LeagueDetailSerializer


class LeagueViewSet(ModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer


class LeagueDetailViewSet(ReadOnlyModelViewSet):
    serializer_class = LeagueDetailSerializer
    queryset = League.objects.select_related('season', 'active_player__profile__user')

    def retrieve(self, request, *args, **kwargs):
        league = self.get_object()

        members_qs = (
            league.members
            .select_related('profile__user')
            .order_by('rank', 'id')
            .prefetch_related(
                Prefetch(
                    'profile__selected_games',
                    queryset=SelectedGame.objects
                    .filter(league=league)
                    .select_related('game'),
                    to_attr='selected_in_this_league',
                ),
                # If you have BanDecision → PlayerProfile with related_name='ban_decisions':
                Prefetch(
                    'profile__ban_decisions',
                    queryset=BanDecision.objects
                    .filter(league=league)
                    .select_related('game'),
                    to_attr='ban_in_this_league',
                ),
                # If your BanDecision uses a different related_name, adjust the line above accordingly.
                # If it has no related_name, use 'profile__bandecision_set' instead.
            )
        )

        # Attach prefetch to this instance
        prefetch_related_objects([league], Prefetch('members', queryset=members_qs))

        serializer = LeagueDetailSerializer(
            league,
            context={'league': league}  # still handy for is_active_player, etc.
        )
        return Response(serializer.data)
