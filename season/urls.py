from django.urls import path

from season.views import SeasonDetailView, SeasonListView, SeasonParticipants

app_name = 'season'

urlpatterns = [
    path('', SeasonListView.as_view(), name='list'),
    path('<pk>', SeasonDetailView.as_view(), name='detail'),
    path('<pk>/participants', SeasonParticipants.as_view(), name='participants'),
]

