from django.conf import settings
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notification.models import PushSubscription
from notification.services import send_test_notification


class PushSubscriptionSerializer(serializers.Serializer):
    endpoint = serializers.URLField(max_length=500)
    keys = serializers.DictField(child=serializers.CharField(), write_only=True)

    def validate_keys(self, value):
        if not value.get("p256dh") or not value.get("auth"):
            raise serializers.ValidationError("Both p256dh and auth keys are required.")
        return value


class VapidPublicKeyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not settings.VAPID_PUBLIC_KEY:
            return Response(
                {"detail": "Push notifications are not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response({"public_key": settings.VAPID_PUBLIC_KEY})


class SendTestNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        result = send_test_notification(request.user)
        if not result["configured"]:
            return Response(
                {"detail": "Push notifications are not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(
            {"targeted": result["targeted"], "succeeded": result["succeeded"]}
        )


class PushSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PushSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        PushSubscription.objects.update_or_create(
            endpoint=serializer.validated_data["endpoint"],
            defaults={
                "user": request.user,
                "p256dh": serializer.validated_data["keys"]["p256dh"],
                "auth": serializer.validated_data["keys"]["auth"],
            },
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request):
        endpoint = request.data.get("endpoint")
        if not endpoint:
            return Response(
                {"detail": "endpoint is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        PushSubscription.objects.filter(user=request.user, endpoint=endpoint).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
