from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.detail import DetailView
from django.shortcuts import render
from django.urls import reverse_lazy
from user.models import User


# Create your views here.

class LoginView(LoginView):
    template_name = 'user/login.html'
    success_url = '/'

class LogoutView(LogoutView):
    next_page=reverse_lazy('home')

class UserProfileView(DetailView):
    template_name = 'user/profile.html'
    model = User
