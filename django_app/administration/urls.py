from django.urls import path

from administration.views import AdministrationView

app_name = 'administration'

urlpatterns = [
    path('', AdministrationView.as_view(), name='manage')
]