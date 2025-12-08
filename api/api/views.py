from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from league.models import LeagueStanding
from user.models import PlatformPlayer

from collections import defaultdict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class LoginApiView(APIView):
    @staticmethod
    def post(request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        # Check if both username and password are provided
        if not username or not password:
            return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        # Check if authentication was successful
        if user is not None:
            # If authentication successful, return user data or token
            # For example, you can return user data or JWT token here
            # print(get_token(user))
            return Response({'message': 'Login successful', "user": get_user_information(user)},
                            status=status.HTTP_200_OK)
        else:
            # If authentication failed, return error message
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutApiView(APIView):
    @staticmethod
    def post(request, *args, **kwargs):
        # Check if the user is authenticated
        token = request.auth  # The token is automatically attached to authenticated requests

        if token:
            # Find and delete the token to log the user out
            try:
                token_object = Token.objects.get(key=token)
                token_object.delete()
                return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
            except Token.DoesNotExist:
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'No token provided or invalid token'}, status=status.HTTP_400_BAD_REQUEST)


# no better place to put currently, maybe lateron in a statistic module
class YearStandingMatrixView(APIView):
    """
    Returns a yearly matrix of league positions per player.

    Query params:
      - year (int, required): e.g. ?year=2025

    Assumptions:
      - League has: season (FK) and level (int; 1 = best league)
      - Season has: start_date (DateField or DateTimeField)

    Response shape:
    {
      "year": 2025,
      "levels": [1, 2, 3],   # distinct league levels used that year (sorted)
      "standings": [
        {
          "player_profile_id": 5,
          "profile_name": "MissM1",
          "per_level": {
            "1": {"first": 3, "second": 1, "third": 0, "fourth": 0},
            "2": {"first": 1, "second": 2, "third": 0, "fourth": 0}
          },
          "totals": {"first": 4, "second": 3, "third": 0, "fourth": 0}
        },
        ...
      ]
    }
    """

    def get(self, request, *args, **kwargs):
        year_param = request.query_params.get("year")
        if not year_param:
            return Response(
                {"detail": "Query parameter 'year' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            year = int(year_param)
        except ValueError:
            return Response(
                {"detail": "Query parameter 'year' must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get all league standings for leagues whose season is in that year
        standings_qs = (
            LeagueStanding.objects
            .filter(
                league__season__year=year,
            )
            .select_related("league", "league__season", "player_profile")
            .order_by("league_id", "-league_points", "-wins", "-points")
        )

        if not standings_qs.exists():
            return Response(
                {"year": year, "levels": [], "standings": []},
                status=status.HTTP_200_OK,
            )

        # Distinct league levels used in that year (sorted, 1 is top)
        levels = sorted(
            standings_qs.values_list("league__level", flat=True).distinct()
        )

        # Aggregation:
        # player_id -> {
        #   "player_profile_id": ...,
        #   "profile_name": ...,
        #   "per_level": {
        #       "1": {"first": ..., "second": ..., "third": ..., "fourth": ...},
        #       "2": {...},
        #       ...
        #   },
        #   "totals": {"first": ..., "second": ..., "third": ..., "fourth": ...}
        # }
        players_stats = {}

        pos_key_for_rank = {1: "first", 2: "second", 3: "third", 4: "fourth"}

        current_league_id = None
        rank_in_league = 0

        for ls in standings_qs:
            # Detect league change so we can reset rank
            if ls.league_id != current_league_id:
                current_league_id = ls.league_id
                rank_in_league = 1
            else:
                rank_in_league += 1

            # Only care about positions 1..4
            if rank_in_league > 4:
                continue

            pos_key = pos_key_for_rank.get(rank_in_league)
            if not pos_key:
                continue

            player_id = ls.player_profile_id
            level = ls.league.level
            level_key = str(level)

            if player_id not in players_stats:
                players_stats[player_id] = {
                    "player_profile_id": player_id,
                    "profile_name": ls.player_profile.profile_name,
                    "per_level": defaultdict(
                        lambda: {"first": 0, "second": 0, "third": 0, "fourth": 0}
                    ),
                    "totals": {"first": 0, "second": 0, "third": 0, "fourth": 0},
                }

            pstats = players_stats[player_id]

            # Ensure this level exists
            _ = pstats["per_level"][level_key]  # triggers default if missing

            # Increment per-level and total counters
            pstats["per_level"][level_key][pos_key] += 1
            pstats["totals"][pos_key] += 1

        # Convert defaultdicts to normal dicts and sort players
        standings_list = []
        for p in players_stats.values():
            per_level_clean = {
                level_key: counts
                for level_key, counts in p["per_level"].items()
            }
            standings_list.append({
                "player_profile_id": p["player_profile_id"],
                "profile_name": p["profile_name"],
                "per_level": per_level_clean,
                "totals": p["totals"],
            })

        # Sort players: most 1st places, then 2nd, 3rd, 4th, then name
        def sort_key(item):
            t = item["totals"]
            return (-t["first"], -t["second"], -t["third"], -t["fourth"], item["profile_name"].lower())

        standings_list.sort(key=sort_key)

        return Response(
            {
                "year": year,
                "levels": levels,
                "standings": standings_list,
            },
            status=status.HTTP_200_OK,
        )


def create_token(user):
    return Token.objects.create(user=user)


def has_token(user):
    return Token.objects.filter(user=user).exists()


def get_token(user):
    if has_token(user):
        token = Token.objects.get(user=user)
    else:
        token = create_token(user)
    return str(token)


def get_user_information(user):
    token = get_token(user)
    user = {
        "username": user.username,
        "admin": user.is_superuser,
        "token": token,
        # "platform_players": get_platform_players(user),
        "profile": {"id": user.profile.id, "name": user.profile.profile_name}
    }
    return user


def get_platform_players(user):
    player_profile = user.profile
    platform_players = PlatformPlayer.objects.filter(player_profile=player_profile)
    platform_player_dict = {pp.platform.name: pp.name for pp in platform_players}
    return platform_player_dict
