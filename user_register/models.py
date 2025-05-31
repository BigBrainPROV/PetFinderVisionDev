from django.contrib.auth.models import User
from django.core.validators import validate_image_file_extension
from django.db import models

from user_register.constants import AnimalsType, SexType, ColorType
from common.validators import phone_regex


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        validators=[validate_image_file_extension],
        verbose_name="avatar",
    )
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="name")
    surname = models.CharField(max_length=255, blank=True, null=True, verbose_name="surname")
    phone = models.CharField(
        validators=[phone_regex],
        max_length=15,
        null=True,
        blank=True,
        unique=True,
        verbose_name="phone",
    )

    class Meta:
        verbose_name = "user profile"
        verbose_name_plural = "users profile"


class PetUserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="pet_profile")
    type = models.PositiveIntegerField(choices=AnimalsType.choices, verbose_name="animal type", blank=True, null=True)
    sex = models.PositiveIntegerField(choices=SexType.choices, verbose_name="sex type", blank=True, null=True)
    breed = models.CharField(max_length=255, blank=True, null=True, verbose_name="breed")
    color = models.PositiveIntegerField(choices=ColorType.choices, verbose_name="color type", blank=True, null=True)
    photo = models.ImageField(
        upload_to="pets/",
        blank=True,
        null=True,
        validators=[validate_image_file_extension],
        verbose_name="photo",
    )

    class Meta:
        verbose_name = "pet user profile"
        verbose_name_plural = "pets users profile"
