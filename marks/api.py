from rest_framework.viewsets import ModelViewSet

from marks.models import Marks
from marks.serializers import MarksSerializer


class MarksViewSet(ModelViewSet):
    queryset = Marks.objects.all()
    serializer_class = MarksSerializer
