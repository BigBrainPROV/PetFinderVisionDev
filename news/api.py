from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

from news.serializers import NewsListSerializer
from news.models import News


class NewsViewSet(ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsListSerializer
    permission_classes = [AllowAny]  # Разрешаем публичный доступ
