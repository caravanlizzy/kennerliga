from django.shortcuts import render
from django.views.generic import CreateView

from match_result.forms import CreateResultForm
from match_result.models import MatchResult


# Create your views here.

class CreateResultView(CreateView):
    template_name = 'match_result/create_result.html'
    model = MatchResult
    form_class = CreateResultForm
