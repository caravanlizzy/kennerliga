import logging


from league.models import League
from season.models import Season
from user.models import PlayerProfile, User, PlatformPlayer


def create_profile_for_user(user):
    profile_name = user.username + "_profile"
    new_profile = PlayerProfile(user=user, profile_name=profile_name)
    new_profile.save()


def create_user(username):
    if User.objects.filter(username=username).exists():
        logging.error(f"User {username} already exists.")
        return
    new_user = User(username=username)
    new_user.save()
    create_profile_for_user(new_user)


def get_user_by_username(username):
    try:
        user = User.objects.get(username=username)
        return user
    except User.DoesNotExist:
        logging.error(f"No user found with the username {username}")
        return None  # Return None if the user does not exist


def get_profile_by_username(username):
    user = get_user_by_username(username)
    if user:
        try:
            return user.profile
        except AttributeError:
            logging.error(f"Profile not found for user with username {username}")
            return None
    return None  # Return None if the user is not found


def create_platform_player(profile, platform):
    if not profile or not platform:
        logging.error("Invalid profile or platform provided")
        return None

    try:
        name = f"{profile.profile_name}_{platform.name}"
        print(name)
        new_platform_player = PlatformPlayer(
            player_profile=profile, platform=platform, name=name
        )
        new_platform_player.save()
        return new_platform_player  # Return the created object
    except Exception as e:
        logging.error(f"Error creating PlatformPlayer: {e}")
        return None


def create_platform_player_by_user(username, platform):
    user = get_user_by_username(username)
    if user:
        create_platform_player(user.profile, platform)


def create_bga_platform_players_based_on_existing_users():
    from .models import Platform  # Lazy import inside the function

    usernames = list(User.objects.all())
    try:
        bga = Platform.objects.get(name="BGA")
        if bga and usernames:
            [create_platform_player_by_user(user.username, bga) for user in usernames]
    except Platform.DoesNotExist:
        logging.error("Platform 'BGA' not found")


def find_users_current_league(profile):
    try:
        # Get the league for the running season
        league = League.objects.get(season__status=Season.SeasonStatus.RUNNING)
        # Check if the profile is a member of the league
        if league.members.filter(profile=profile).exists():
            return league
        return None
    except PlayerProfile.DoesNotExist:
        return None  # No matching profile found
    except League.DoesNotExist:
        return None  # No league found for the running season
    except League.MultipleObjectsReturned:
        raise ValueError("Multiple leagues found for the current running season.")


def get_user_summary_stats(user):
    """
    Calculates summary statistics for a user:
    - win_rate: percentage of games where position == 1 among positioned games (float, rounded to 1 decimal place), or None if no games played.
    - avg_position: average position among positioned games (float, rounded to 2 decimal places), or None if no games played.
    - most_participated_league_level: league level integer with the most participations for the user, or None if no participations.
    """
    profile = getattr(user, "profile", None)
    if not profile:
        return {
            "win_rate": None,
            "avg_position": None,
            "most_participated_league_level": None,
        }

    from result.models import Result
    from django.db.models import Avg, Count, Q

    res_agg = Result.objects.filter(
        player_profile=profile, position__isnull=False
    ).aggregate(
        avg_pos=Avg("position"),
        total_games=Count("id"),
        wins=Count("id", filter=Q(position=1)),
    )

    total_games = res_agg["total_games"] or 0
    wins = res_agg["wins"] or 0
    avg_pos = res_agg["avg_pos"]

    win_rate = round((wins / total_games) * 100, 1) if total_games > 0 else None
    avg_position = round(avg_pos, 2) if avg_pos is not None else None

    top_level = (
        League.objects.filter(
            Q(members__profile=profile)
            | Q(standings__player_profile=profile)
            | Q(results__player_profile=profile)
        )
        .values("level")
        .annotate(count=Count("id", distinct=True))
        .order_by("-count", "level")
        .first()
    )
    most_participated_level = top_level["level"] if top_level else None

    return {
        "win_rate": win_rate,
        "avg_position": avg_position,
        "most_participated_league_level": most_participated_level,
    }
