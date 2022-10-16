from django.contrib.auth.views import LoginView
from django.shortcuts import render


# Create your views here.

class LoginView(LoginView):
    template_name = 'login.html'
    success_url = '/'
