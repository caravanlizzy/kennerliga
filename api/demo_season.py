import os
import django

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_rest.settings')

# Initialize Django
django.setup()

from season_manager import start_new_season

# start_new_season()

selected_games = [
    {'id': 't'}
]


def create_demo_season():
    return
