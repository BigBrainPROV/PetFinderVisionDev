from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

from feedback.models import Feedback
from feedback.serializers import FeedbackSerializer


class FeedbackViewSet(ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [AllowAny]  # Разрешаем публичный доступ

    def get_queryset(self):
        return Feedback.objects.all().order_by('-id')
