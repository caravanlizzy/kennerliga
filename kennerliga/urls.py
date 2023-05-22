"""kennerliga URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin

from django.urls import include, path

from game.views import NewGameView
from home.views import HomeView, AddSeasonParticipantView, RemoveSeasonParticipantView
from match_result.views import CreateResultView
from user.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', HomeView.as_view(), name='home'),
    path('add-participant', AddSeasonParticipantView.as_view(), name='add-participant'),
    path('remove-participant', RemoveSeasonParticipantView.as_view(), name='remove-participant'),
    path('administration/', include('administration.urls')),
    path('post-result/', CreateResultView.as_view(), name='post-result'),
    path('users/', include('user.urls')),
    path('games/', include('game.urls')),
    path('seasons/', include('season.urls')),
]
