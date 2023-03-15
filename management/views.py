from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.
class ManagementView(TemplateView):
    template_name = 'management/manage.html'
