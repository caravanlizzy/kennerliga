import os
import django

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_rest.settings')

# Initialize Django
django.setup()


from season_manager import SeasonManager

manager = SeasonManager()

print(manager.current_season)
print(manager.open_season)

def create_demo_season():
    return


