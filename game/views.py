from django.urls import reverse_lazy

# Create your views here.
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from game.models import Game, GameSettingsCategory


class NewGameView(CreateView):
    model = Game
    fields = '__all__'
    template_name = 'game/new_game.html'
    success_url = reverse_lazy('game:games')


class GameDetailView(DetailView):
    model = Game
    fields = '__all__'
    template_name = 'game/game_detail.html'


class GameListView(ListView):
    model = Game
    template_name = 'game/games_list.html'


class NewGameOption(CreateView):
    model = GameSettingsCategory
    fields = '__all__'
    template_name = 'game/new_game_option.html'
