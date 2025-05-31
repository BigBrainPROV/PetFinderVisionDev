from rest_framework import serializers

from advertisements.models import Advertisement


class AdvertisementListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = [
            "id",
            "title",
            "description",
            "author",
            "photo",
            "phone",
            "status",
            "type",
            "location",
            "latitude",
            "longitude",
            "created_at",
        ]


class AdvertisementRetrieveSerializer(AdvertisementListSerializer):
    class Meta:
        model = Advertisement
        fields = AdvertisementListSerializer.Meta.fields + [
            "breed",
            "color",
            "sex",
            "social_media",
            "eye_color",
            "face_shape",
            "special_features",
            "updated_at",
        ]


class AdvertisementCreateSerializer(serializers.ModelSerializer):
    breed = serializers.CharField()
    color = serializers.ChoiceField(choices=Advertisement._meta.get_field('color').choices)
    sex = serializers.ChoiceField(choices=Advertisement._meta.get_field('sex').choices)
    type = serializers.CharField()
    status = serializers.ChoiceField(choices=Advertisement._meta.get_field('status').choices)
    social_media = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    eye_color = serializers.ChoiceField(choices=Advertisement._meta.get_field('eye_color').choices)
    face_shape = serializers.ChoiceField(choices=Advertisement._meta.get_field('face_shape').choices)
    special_features = serializers.ChoiceField(choices=Advertisement._meta.get_field('special_features').choices)
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    location = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Advertisement
        fields = AdvertisementListSerializer.Meta.fields + [
            "breed",
            "color",
            "sex",
            "social_media",
            "eye_color",
            "face_shape",
            "special_features",
            "latitude",
            "longitude",
            "location",
        ]

    def create(self, validated_data):
        return Advertisement.objects.create(**validated_data)
