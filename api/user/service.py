import logging

from user.models import User, PlayerProfile, PlatformPlayer


def create_profile_for_user(user):
    profile_name = user.username + '_profile'
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
        name = f"{profile.name}_{platform.name}"
        new_platform_player = PlatformPlayer(player_profile=profile, platform=platform, name=name)
        new_platform_player.save()
        return new_platform_player  # Return the created object
    except Exception as e:
        logging.error(f"Error creating PlatformPlayer: {e}")
        return None


def get_profile_by_username(username):
    return get_user_by_username(username).profile


def create_platform_player(profile, platform):
    if not profile or not platform:
        logging.error("Invalid profile or platform provided")
        return None

    try:
        name = f"{profile.profile_name}_{platform.name}"
        print(name)
        new_platform_player = PlatformPlayer(player_profile=profile, platform=platform, name=name)
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
        bga = Platform.objects.get(name='BGA')
        if bga and usernames:
            [create_platform_player_by_user(user.username, bga) for user in usernames]
    except Platform.DoesNotExist:
        logging.error("Platform 'BGA' not found")
