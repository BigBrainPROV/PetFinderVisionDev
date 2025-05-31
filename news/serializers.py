from rest_framework.serializers import ModelSerializer

from news.models import News


class NewsListSerializer(ModelSerializer):
    class Meta:
        model = News
        fields = ("id", "title", "description", "created_at")
