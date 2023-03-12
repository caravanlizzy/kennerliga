from django.urls import path

from management.views import ManagementView

app_name = 'management'

urlpatterns = [
    path('', ManagementView.as_view(), name='manage')
]