from django.urls import path

from notification.views import PushSubscriptionView, VapidPublicKeyView

urlpatterns = [
    path("vapid-public-key/", VapidPublicKeyView.as_view()),
    path("subscriptions/", PushSubscriptionView.as_view()),
]
