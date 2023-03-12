from django.urls import path

from game.views import NewGameView, GameDetailView, GameListView

app_name = 'game'

urlpatterns = [
    path('new', NewGameView.as_view(), name='new-game'),
    path('detail/<pk>', GameDetailView.as_view(), name='game-detail'),
    path('', GameListView.as_view(), name='games'),
]
