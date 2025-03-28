from rest_framework.viewsets import ModelViewSet
from league.models import League
from league.serializer import LeagueSerializer
from rest_framework.views import APIView, Response, status
from league.service import next_player
from django.shortcuts import get_object_or_404

class LeagueViewSet(ModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer


class SelectGameView(APIView):
    def post(self, request, league_id):
        league = get_object_or_404(League, id=league_id)
        new_active_player = next_player(league)

        if new_active_player is None:
            return Response({"detail": "No members in the league."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": f"Next player is now {new_active_player.profile.user.username}.",
            "player_id": new_active_player.id,
            "player_name": new_active_player.profile.user.username
        }, status=status.HTTP_200_OK)
