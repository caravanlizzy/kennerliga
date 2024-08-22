from django.urls import path

from season.views import SeasonRegistrationView

urlpatterns = [
    path('register/', SeasonRegistrationView.as_view())
]

