from rest_framework import serializers
from django.core.exceptions import ValidationError
import os

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

    def validate_photo(self, value):
        """
        Валидация загружаемого фото
        """
        if value:
            # Проверка размера файла (максимум 10 МБ)
            max_size = 10 * 1024 * 1024  # 10 МБ
            if value.size > max_size:
                raise serializers.ValidationError(
                    'Размер файла слишком большой. Максимальный размер: 10 МБ'
                )
            
            # Проверка типа файла
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in allowed_extensions:
                raise serializers.ValidationError(
                    'Неподдерживаемый формат файла. Разрешены: JPG, PNG, WebP'
                )
            
            # Проверка MIME типа
            allowed_types = ['image/jpeg', 'image/png', 'image/webp']
            if hasattr(value, 'content_type') and value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    'Неподдерживаемый тип файла. Загрузите изображение в формате JPG, PNG или WebP'
                )
        
        return value

    def create(self, validated_data):
        return Advertisement.objects.create(**validated_data)
