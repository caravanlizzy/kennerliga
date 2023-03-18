from django.forms import formset_factory
from django.urls import reverse_lazy, reverse

# Create your views here.
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from game.forms import NewOptionForm
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


class NewGameSettingsCategory(CreateView):
    model = GameSettingsCategory
    template_name = 'game/new_game_option.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse('game:game-detail', kwargs={'pk': 1})

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['newOptionForm'] = formset_factory(NewOptionForm)()
        return context_data

    def form_valid(self, form):
        print('valid!')
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)
