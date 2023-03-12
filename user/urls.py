from django.urls import path

from user.views import RegisterUserView, UserProfileView, UserListView

app_name = 'user'

urlpatterns = [
    path('profile/<int:pk>', UserProfileView.as_view(), name='profile'),
    path('register', RegisterUserView.as_view(), name='register'),
    path('users', UserListView.as_view(), name='users'),
]
