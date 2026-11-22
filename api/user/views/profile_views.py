from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from league.models import League, LeagueStatus
from league.serializer import LeagueMinimalSerializer
from result.models import Result
from result.serializers import ResultSerializer
from season.models import Season, SeasonParticipant


class MeViewSet(ViewSet):
    """
    API viewset for the current authenticated user's context.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="current-league")
    def current_league(self, request):
        """
        Returns the current running league for the authenticated user.
        """
        profile = request.user.profile

        participant = (
            SeasonParticipant.objects.filter(
                profile=profile, season__status=Season.SeasonStatus.RUNNING
            )
            .select_related("season")
            .first()
        )

        if not participant:
            return Response(
                {"detail": "No running season participation found."}, status=404
            )

        league = League.objects.filter(
            members=participant, season=participant.season
        ).first()

        if not league:
            return Response(
                {"detail": "No league found for current season."}, status=404
            )

        data = LeagueMinimalSerializer(league).data
        data["is_my_turn"] = (
            league.status
            in (
                LeagueStatus.PICKING,
                LeagueStatus.BANNING,
                LeagueStatus.REPICKING,
            )
            and league.active_player_id == participant.id
        )
        return Response(data)

    @action(detail=False, methods=["get"], url_path="results")
    def results(self, request):
        """
        Returns all game results for the authenticated user.
        """
        results = Result.objects.filter(player_profile=request.user.profile)
        return Response(ResultSerializer(results, many=True).data)
