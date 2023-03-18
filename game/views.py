from django.forms import formset_factory
from django.urls import reverse_lazy, reverse

# Create your views here.
from django.views.generic import CreateView, DetailView, ListView, FormView
from betterforms.multiform import MultiForm

from game.forms import GameSettingsForm
from game.models import Game, GameSettingsCategory, GameSettingsOption


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


class GameSettingsView(FormView):
    template_name = 'game/new_game_option.html'
    form_class = GameSettingsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = Game.objects.get(pk=self.kwargs.get('pk'))
        return context

    def get_success_url(self):
        return reverse('game:game-detail', kwargs={'pk': self.kwargs.get('pk')})

    def form_valid(self, form):
        is_bool = False
        if not form.data['options-0-option']:
            is_bool = True
        category = GameSettingsCategory(game_id=self.kwargs.get('pk'), name=form.data['category-name'], is_bool=is_bool)
        category.save()
        if not is_bool:
            for i in range(int(form.data['options-TOTAL_FORMS'])):
                option = GameSettingsOption(category_id=category.id, option=form.data[f'options-{str(i)}-option'])
                option.save()
        return super().form_valid(form)
