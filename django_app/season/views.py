from django.views.generic import DetailView, ListView

from season.models import Season
from user.models import User


# Create your views here.
class SeasonDetailView(DetailView):
    model = Season
    template_name = 'season/season_detail.html'


class SeasonListView(ListView):
    model = Season
    template_name = 'season/season_list.html'

    def get_queryset(self):
        return Season.objects.order_by('-year', '-month')


class SeasonParticipants(ListView):
    model = User
    template_name = 'season/participants_list.html'

    def get_queryset(self, **kwargs):
        return User.objects.filter(seasons_participating__id=self.kwargs['pk'])
