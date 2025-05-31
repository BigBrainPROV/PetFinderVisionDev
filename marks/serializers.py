from rest_framework.serializers import ModelSerializer

from marks.models import Marks


class MarksSerializer(ModelSerializer):
    class Meta:
        model = Marks
        fields = '__all__'
