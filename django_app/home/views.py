# Create your views here.
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView, UpdateView

from season.models import Season
import logging

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = 'home/home.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if 'open_season' in context:
            context['user_is_registered'] = request.user in context['open_season'].participants.all()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        open_season = get_open_season()
        if open_season:
            context['open_season'] = open_season
        context['current_year'] = datetime.today().year
        return context


class AddSeasonParticipantView(View):
    http_method_names = ['patch', 'put']

    def dispatch(self, request, *args, **kwargs):
        open_season = get_open_season()
        open_season.participants.add(request.user)
        open_season.save()
        return redirect('home')


class RemoveSeasonParticipantView(View):
    http_method_names = ['patch', 'put']

    def dispatch(self, request, *args, **kwargs):
        open_season = get_open_season()
        open_season.participants.remove(request.user)
        open_season.save()
        return redirect('home')


def get_open_season():
    open_season = Season.objects.filter(status=Season.SeasonStatus.OPEN)
    if (len(open_season)) == 1:
        return open_season[0]
    elif len(open_season) > 1:
        logger.error('More than one open seasons found.')
    elif len(open_season) == 0:
        logger.error('No open season found')
    else:
        raise AttributeError
