
# Create your views here.
from django.views.generic import TemplateView

from season.models import Season


class HomeView(TemplateView):
    template_name = 'home/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        open_season = Season.objects.filter(status=Season.SeasonStatus.OPEN)
        if open_season:
            context['open_season'] = open_season
        return context
