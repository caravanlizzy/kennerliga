from django.urls import path

from user.views import RegisterUserView, UserProfileView

urlpatterns = [
    path('user/profile/<int:pk>', UserProfileView.as_view(), name='profile'),
    path('user/register', RegisterUserView.as_view(), name='register'),
]