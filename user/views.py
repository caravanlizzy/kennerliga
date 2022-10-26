from django.contrib.auth.views import LoginView
from django.views.generic.detail import DetailView
from django.shortcuts import render
from user.models import User


# Create your views here.

class LoginView(LoginView):
    template_name = 'login.html'
    success_url = '/'


class UserProfileView(DetailView):
    template_name = 'user/profile.html'
    model = User
