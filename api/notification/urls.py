from django.urls import path

from notification.views import (
    PushSubscriptionView,
    SendTestNotificationView,
    VapidPublicKeyView,
)

urlpatterns = [
    path("vapid-public-key/", VapidPublicKeyView.as_view()),
    path("subscriptions/", PushSubscriptionView.as_view()),
    path("test/", SendTestNotificationView.as_view()),
]
