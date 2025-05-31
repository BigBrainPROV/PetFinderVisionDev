from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from user_register.models import UserProfile, PetUserProfile


class PetUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetUserProfile
        fields = [
            "type",
            "sex",
            "breed",
            "color",
            "photo"
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "name",
            "surname",
            "phone",
            "avatar"
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    pet_profile = PetUserProfileSerializer(required=False)
    email = serializers.EmailField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "profile", "pet_profile"]
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
            "email": {"write_only": True, "required": False},
            "profile": {"required": False},
            "pet_profile": {"required": False},
        }

    def update(self, instance, validated_data):
        profile_data = validated_data.get("profile", {})
        pet_profile_data = validated_data.get("pet_profile", {})
        profile_serializer = UserProfileSerializer(
            instance=instance.profile,
            data=profile_data
        )
        profile_serializer.is_valid(raise_exception=True)
        profile_serializer.save()
        pet_profile_serializer = PetUserProfileSerializer(
            instance=instance.pet_profile,
            data=pet_profile_data
        )
        pet_profile_serializer.is_valid(raise_exception=True)
        pet_profile_serializer.save()

        return instance

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
