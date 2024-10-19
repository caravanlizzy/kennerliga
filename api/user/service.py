import logging
from user.models import PlayerProfile, User


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
