from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from user.models import Feedback
from user.serializers import FeedbackSerializer


class FeedbackViewSet(ModelViewSet):
    """
    API viewset for submitting and viewing user feedback.
    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
