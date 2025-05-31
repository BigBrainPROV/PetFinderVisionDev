from rest_framework import serializers

from feedback.models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            'id',
            'name',
            'message',
        ]
        read_only_fields = ['id']
        write_only_fields = ['name', 'message']
