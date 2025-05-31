from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from user_register.serializers import UserSerializer
from user_register.models import UserProfile
from user_register.constants import (
    CAT_BREEDS, DOG_BREEDS, BIRD_BREEDS, RODENT_BREEDS,
    RABBIT_BREEDS, REPTILE_BREEDS, OTHER_BREEDS
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_staff=False)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.pk != request.user.id:
            raise ValidationError("You do not have permission to perform this action")
        if request.data.get("profile", {}):
            if instance.profile.phone == request.data.get("profile", {}).get("phone"):
                request.data["profile"].pop("phone")
        return super().update(request, *args, **kwargs)

    @action(methods=["get"], detail=False)
    def breeds(self, request):
        """
        Получить список пород в зависимости от типа животного.
        """
        animal_type = request.query_params.get('type')
        
        breeds_map = {
            'cat': CAT_BREEDS,
            'dog': DOG_BREEDS,
            'bird': BIRD_BREEDS,
            'rodent': RODENT_BREEDS,
            'rabbit': RABBIT_BREEDS,
            'reptile': REPTILE_BREEDS,
            'other': OTHER_BREEDS
        }
        
        return Response(breeds_map.get(animal_type, []))

    @action(methods=["get", "post"], detail=False)
    def current(self, request, *args, **kwargs):
        """
        GET: Получить данные текущего пользователя.
        POST: Обновить данные текущего пользователя.
        """
        if request.method == "GET":
            if not request.user.is_authenticated:
                return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        
        elif request.method == "POST":
            if not request.user.is_authenticated:
                return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
            
            profile_data = request.data.get("profile", {})
            if not profile_data:
                raise ValidationError("Profile data is required")
            
            user = request.user
            profile = user.profile
            
            # Update profile fields
            for field in ["name", "surname", "phone"]:
                if field in profile_data:
                    setattr(profile, field, profile_data[field])
            
            # Validate phone uniqueness if it's being updated
            if "phone" in profile_data:
                existing_profile = UserProfile.objects.filter(phone=profile_data["phone"]).exclude(user=user).first()
                if existing_profile:
                    raise ValidationError({"phone": "This phone number is already in use"})
            
            profile.save()
            
            serializer = self.get_serializer(user)
            return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
    )
    def avatar(self, request):
        """
        Загрузить новый аватар текущего пользователя.
        """

        file = request.data["file"]
        profile = request.user.profile

        profile.avatar = file
        profile.save(update_fields=["avatar"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["post"],
    )
    def pet_photo(self, request):
        """
        Загрузить фотографию петомца для текущего пользователя.
        """
        file = request.data["file"]
        pet_profile = request.user.pet_profile

        pet_profile.photo = file
        pet_profile.save(update_fields=["photo"])

        return Response(status=status.HTTP_204_NO_CONTENT)
