from django.urls import path

from game.views import NewGameView, GameDetailView, GameListView, GameSettingsView

app_name = 'game'

urlpatterns = [
    path('new', NewGameView.as_view(), name='new-game'),
    path('detail/<pk>', GameDetailView.as_view(), name='game-detail'),
    path('list', GameListView.as_view(), name='games'),
    path('detail/<pk>/option/new', GameSettingsView.as_view(), name='new-option'),
]
