from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from season.serializer import TLiveEventSerializer
from season.services import build_live_events_timeline


class LiveEventViewSet(ViewSet):
    """
    API viewset for retrieving a live timeline of events (picks, bans, finishes) in a season.
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        league_id = request.query_params.get("league_id")
        season_id = request.query_params.get("season_id")
        limit = request.query_params.get("limit")

        events = build_live_events_timeline(
            league_id=league_id,
            season_id=season_id,
            limit=limit,
        )

        serializer = TLiveEventSerializer(events, many=True)
        return Response(serializer.data)
